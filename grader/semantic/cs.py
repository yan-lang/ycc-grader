import datetime
import logging
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from jinja2 import Template

from ..common import BaseReport, BaseGrader, Runner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ControlStructure Grader")


class ControlStructureGrader(BaseGrader):
    def get_runner(self) -> Runner:
        return Runner("cs", "cs_out", "xml", logger)

    def grade_single(self, stu_out, gold_out) -> BaseReport:
        stu_css = self._parse_(stu_out)
        gold_css = self._parse_(gold_out)

        result = []
        for gold_cs in gold_css:
            passed = False
            for stu_cs in stu_css:
                if stu_cs == gold_cs:
                    passed = True
                    stu_cs.passed = True
                    gold_cs.passed = True
            result.append(passed)

        return CSReport(result, gold_css, stu_css)

    @staticmethod
    def _parse_(out_path):
        css = []
        cs = ET.parse(out_path).getroot()
        for item in cs.iter("break"):
            css.append(ControlStructure(item.findtext('line'),
                                        'break',
                                        item.findtext('attachedLoop')))
        for item in cs.iter("continue"):
            css.append(ControlStructure(item.findtext('line'),
                                        'continue',
                                        item.findtext('attachedLoop')))
        for item in cs.iter("return"):
            css.append(ControlStructure(item.findtext('line'),
                                        'continue',
                                        item.findtext('attachedFunction')))
        return css


class ControlStructure:
    def __init__(self, line, type, def_line):
        self.line = line
        self.type = type
        self.def_line = def_line
        self.passed = False

    def __eq__(self, other):
        if type(other) != ControlStructure:
            return False
        return self.line == other.line and self.type == other.type and self.def_line == other.def_line

    def __str__(self):
        return "ControlStructure(line={0}, type={1}, def_line={2})".format(self.line, self.type, self.def_line)

    @property
    def status(self):
        return "correct" if self.passed else "incorrect"


class CSReport(BaseReport):

    def __init__(self, grade_result, gold_css, stu_css):
        self._grade = int(grade_result.count(True) / len(grade_result) * self.total_grade)
        self.gold_css = gold_css
        self.stu_css = stu_css
        self.creation_date = datetime.datetime.now()
        self.correct_num = grade_result.count(True)

    @property
    def report_name(self):
        return "control structure analyze"

    @property
    def total_grade(self):
        return 100

    @property
    def grade(self):
        return self._grade

    @property
    def detail(self):
        return self.render()

    def render(self):
        with open(os.path.join(Path(__file__).parent.absolute(), 'cs_report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   grade=self.grade,
                                   total_grade=self.total_grade,
                                   stu_total=len(self.stu_css),
                                   gold_total=len(self.gold_css),
                                   correct_num=self.correct_num,
                                   units=self.stu_css)
