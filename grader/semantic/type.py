import datetime
import logging
import os
from pathlib import Path

from jinja2 import Template
from xmldiff import main, formatting

from ..common import Runner, BaseGrader, BaseReport

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Type Check Grader")


class TypeCheckGrader(BaseGrader):

    def get_runner(self) -> Runner:
        return Runner(target='type', output_dir='type_out', output_extension='xml', logger=logger)

    def grade_single(self, stu_out, gold_out) -> BaseReport:
        formatter = formatting.DiffFormatter()
        diff = main.diff_files(stu_out, gold_out, formatter=formatter, diff_options={'F': 0.5})
        return TypeCheckReport(os.path.basename(stu_out), diff)


class TypeCheckReport(BaseReport):

    def __init__(self, report_name, diff):
        self._report_name = report_name
        self.creation_date = datetime.datetime.now()
        self.diff = diff

    @property
    def report_name(self):
        return self._report_name

    @property
    def total_grade(self):
        return 100

    @property
    def grade(self):
        return 100 if self.diff == '' else 0

    @property
    def detail(self):
        with open(os.path.join(Path(__file__).parent.absolute(), 'type_report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   status="passed" if self.grade == 100 else "not passed",
                                   detail=self.diff if self.diff != '' else "null")
