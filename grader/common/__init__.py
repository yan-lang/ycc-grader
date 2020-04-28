import json
import os
import subprocess

from .util import remove_extension
from abc import ABC, abstractmethod


class BaseRunner(ABC):
    """
    Runner负责执行程序并得到输出

    ```shell
    java [security] [--enable-preview] -jar [jar_path] [options] -o [output] [input]
    ```
    """

    def __init__(self, test_code_dir, logger):
        self.logger = logger

        # 测试文件文件路径
        self.test_cases = self._get_test_cases_(test_code_dir)

        # 构造运行命令
        self.runner = ['java']
        # self.runner.extend(['-Djava.security.manager'])
        # self.runner.extend(['-Djava.security.policy==myapp.policy'])
        self.runner.extend(['--enable-preview', '-jar'])

    def run(self, jar_path, out_dir):
        output_dir = os.path.join(out_dir, self.get_output_dir_name())
        os.makedirs(output_dir, exist_ok=True)

        for test_case in self.test_cases:
            self.logger.info('processing ' + test_case)

            base_name = remove_extension(os.path.basename(test_case))
            cmd = self.runner + [jar_path, test_case, '--target', self.get_target(), '-o',
                                 os.path.join(output_dir, base_name + "." + self.get_output_extension())]

            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
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

    @staticmethod
    def _get_test_cases_(test_code_dir):
        test_cases = []
        for file_name in os.listdir(test_code_dir):
            if file_name.startswith('.'):
                continue
            test_cases.append(os.path.join(test_code_dir, file_name))
        return test_cases

    @abstractmethod
    def get_output_dir_name(self):
        pass

    @abstractmethod
    def get_target(self):
        pass

    @abstractmethod
    def get_output_extension(self):
        pass


class BaseGrader(ABC):

    @abstractmethod
    def grade(self, submitted_file):
        pass
