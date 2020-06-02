# coding=utf-8
"""
    语法分析自动评测脚本 v1.0

    - 脚本假设输入XML为正确格式
"""
import datetime
import logging
import os
from pathlib import Path

from jinja2 import Template

from ..common import Runner, BaseGrader, BaseReport
from xmldiff import main, formatting

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Parser Grader")


class ParserGrader(BaseGrader):

    def get_runner(self) -> Runner:
        return Runner(target='parse', output_dir='parse_out', output_extension='xml', logger=logger)

    def grade_single(self, stu_out, gold_out) -> BaseReport:
        formatter = formatting.DiffFormatter()
        diff_text = main.diff_files(stu_out, gold_out, formatter=formatter, diff_options={'F': 0.5})

        # Compute similarity

        # InsertNode, DeleteNode, MoveNode,
        # InsertAttrib, DeleteAttrib, RenameAttrib, UpdateAttrib,
        # UpdateTextIn, UpdateTextAfter

        diff = main.diff_files(stu_out, gold_out, diff_options={'F': 0.5})

        return ParserReport(os.path.basename(stu_out), diff_text, 0)


class ParserReport(BaseReport):

    def __init__(self, report_name, diff, similarity):
        self._report_name = report_name
        self.diff = diff
        self.creation_date = datetime.datetime.now()
        self.similarity = similarity

    @property
    def report_name(self):
        return self._report_name

    @property
    def total_grade(self):
        return BaseReport.TOTAL_GRADE

    @property
    def grade(self):
        return 100 if self.diff == '' else 0

    @property
    def detail(self):
        with open(os.path.join(Path(__file__).parent.absolute(), 'parse_report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   status="passed" if self.grade == 100 else "not passed",
                                   detail=self.diff if self.diff != '' else "null")
