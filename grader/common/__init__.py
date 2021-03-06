import json
import os
import subprocess
import pathlib

from .report import ErrorReport, BaseReport
from .util import remove_extension, check_extension, load_json
from abc import ABC, abstractmethod


class Runner:
    """
    Runner负责执行程序并得到输出

    ```shell
    java [security] [--enable-preview] -jar [jar_path] [options] -o [output] [input]
    ```
    """

    def __init__(self, target, output_dir, output_extension, logger):
        self.target = target
        self.output_dir = output_dir
        self.output_extension = output_extension
        self.logger = logger

        policy_file = os.path.join(pathlib.Path(__file__).parent.absolute(), 'judge.policy')
        self.vm_args = ['--enable-preview', '-jar']
        # self.vm_args += ['-Djava.security.manager', '-Djava.security.policy=' + policy_file]

    def _cmd_(self, app_path, app_args):
        return ['java'] + self.vm_args + [app_path] + app_args

    def run(self, jar_path, test_code_dir, out_dir):
        # 测试文件文件路径
        test_cases = listdirpath(test_code_dir, 'c')

        output_dir = os.path.join(out_dir, self.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        for test_case in test_cases:
            self.logger.info('processing ' + test_case)

            base_name = remove_extension(os.path.basename(test_case))
            app_args = [test_case, '--target', self.target, '-o',
                        os.path.join(output_dir, base_name + "." + self.output_extension)]

            p = subprocess.Popen(self._cmd_(jar_path, app_args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=False)
            try:
                stdout, stderr = p.communicate(timeout=10)
                status = {"return_code": p.returncode,
                          "stdout": stdout.decode(encoding="utf-8", errors="strict"),
                          "stderr": stderr.decode(encoding="utf-8", errors="strict")}
            except subprocess.TimeoutExpired:
                p.kill()
                status = {"return_code": 1,
                          "stdout": "",
                          "stderr": "time out"}

            with open(os.path.join(output_dir, base_name + '.json'), 'w') as f:
                json.dump(status, f)
        return output_dir


def listdirpath(path, ext):
    """
    Similar to os.listdir, but return full path rather than file name.

    :param path: dir path
    :return: list of file paths in this directory
    """
    file_paths = []
    for file_name in os.listdir(path):
        if file_name.startswith('.'):
            continue
        if not file_name.endswith('.' + ext):
            continue
        file_paths.append(os.path.join(path, file_name))
    return file_paths


class Grader(ABC):
    def __init__(self, test_code_dir, test_gold_dir):
        self.test_code_dir = test_code_dir
        self.test_gold_dir = test_gold_dir

    @abstractmethod
    def grade(self, submitted_file):
        pass


class BaseGrader(Grader):
    def __init__(self, test_code_dir, test_gold_dir):
        super().__init__(test_code_dir, test_gold_dir)
        self.runner = self.get_runner()

    def grade(self, submitted_file):
        check_extension(submitted_file, ('.jar', '.zip'))

        output_dir = os.path.dirname(submitted_file)
        lex_out_dir = self.runner.run(submitted_file, self.test_code_dir, output_dir)

        # Grade output
        reports = []
        for out_name in os.listdir(self.test_gold_dir):
            if not out_name.endswith('.xml'):
                continue
            status = load_json(os.path.join(lex_out_dir, out_name[:-4] + '.json'))
            msg = "stdout:\n{0}\n\nstderr:\n{1}".format(status['stdout'], status["stderr"])

            # return code并不可靠, 即使return code=0不一定能保证stu_out_path, gold_out_path存在
            stu_out_path = os.path.join(lex_out_dir, out_name)
            gold_out_path = os.path.join(self.test_gold_dir, out_name)

            try:
                if os.path.exists(stu_out_path) and os.path.exists(gold_out_path):
                    reports.append(self.grade_single(stu_out_path, gold_out_path))
                else:
                    reports.append(ErrorReport(out_name, BaseReport.TOTAL_GRADE, msg))
            except Exception as e:
                reports.append(ErrorReport(out_name, BaseReport.TOTAL_GRADE, msg + "\n\n" + str(e)))

        return reports

    @abstractmethod
    def grade_single(self, stu_out, gold_out) -> BaseReport:
        pass

    @abstractmethod
    def get_runner(self) -> Runner:
        pass
