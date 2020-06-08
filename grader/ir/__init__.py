import datetime
import logging
import os
import subprocess
from pathlib import Path

from jinja2 import Template

from ..common import BaseReport, Grader, check_extension, listdirpath

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Intermediate Code Grader")


class IRGrader(Grader):
    """
    run `xx.jar -t interpret -o tmp.out test.c`
    - we don't care about output file actually
    - redirect stdin and stdout
    """

    def grade(self, submitted_file):
        check_extension(submitted_file, ('.jar', '.zip'))
        self.submitted_file = submitted_file

        reports = []
        for test_case in listdirpath(self.test_code_dir, 'c'):
            reports.append(self.__grade_single__(test_case))

        return reports

    def __grade_single__(self, test_case):
        basename = os.path.basename(test_case)[:-2]
        dirname = os.path.dirname(test_case)

        data_dir = os.path.join(dirname, basename)
        input_dir = os.path.join(data_dir, 'input')
        output_dir = os.path.join(data_dir, 'output')

        report = IRReport(basename)
        for input_path in listdirpath(input_dir, 'in'):
            input_basename = os.path.basename(input_path)[:-3]
            output_path = os.path.join(output_dir, input_basename + '.out')

            input_data = read_file_content(input_path)
            output_data = read_file_content(output_path)

            cmd = ['java', '--enable-preview', '-jar', self.submitted_file, '--target', 'interpret', test_case]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            try:
                stdout, stderr = p.communicate(input=input_data, timeout=10)
                if stderr != '':
                    report.msgs.append(input_basename + " fail(runtime error): " + stderr)
                elif stdout.strip() != output_data.strip():
                    report.msgs.append(input_basename + " fail(wrong answer)")
                else:
                    report.msgs.append(input_basename + " passed")
                    report.num_passed += 1
            except subprocess.TimeoutExpired:
                p.kill()
                report.msgs.append(input_basename + " fail(timeout)")

            report.num_test_cases += 1

        return report


def read_file_content(path):
    with open(path, 'r') as f:
        return f.read()


class IRReport(BaseReport):

    def __init__(self, report_name):
        self._report_name = report_name
        self.creation_date = datetime.datetime.now()
        self.msgs = []
        self.num_test_cases = 0
        self.num_passed = 0
        self.wa_num = 0
        self.timeout_num = 0
        self.re_num = 0

    @property
    def report_name(self):
        return self._report_name

    @property
    def total_grade(self):
        return BaseReport.TOTAL_GRADE

    @property
    def grade(self):
        return int(self.num_passed / self.num_test_cases * self.total_grade)

    @property
    def detail(self):
        with open(os.path.join(Path(__file__).parent.absolute(), 'report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   file_name=self._report_name,
                                   correct_num=self.num_passed,
                                   total=self.num_test_cases,
                                   wa_num=self.wa_num,
                                   timeout_num=self.timeout_num,
                                   re_num=self.re_num,
                                   msgs=self.msgs)

    def __str__(self):
        return "{0}[{1}/{2}]: {3}".format(self.report_name, self.grade, self.total_grade, self.detail)
