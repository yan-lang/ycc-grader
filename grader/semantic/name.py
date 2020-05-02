import datetime
import logging
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from jinja2 import Template

from ..common import BaseReport, BaseGrader, Runner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NameResolve Grader")


class NameResolveGrader(BaseGrader):
    def get_runner(self) -> Runner:
        return Runner("name", "name_out", "xml", logger)

    def grade_single(self, stu_out, gold_out) -> BaseReport:
        stu_names = self._parse_(stu_out)
        gold_names = self._parse_(gold_out)

        result = []
        for gold_name in gold_names:
            passed = False
            for stu_name in stu_names:
                if stu_name == gold_name:
                    passed = True
                    stu_name.passed = True
                    gold_name.passed = True
            result.append(passed)

        return NameReport(result, gold_names, stu_names)

    @staticmethod
    def _parse_(out_path):
        name = []
        root = ET.parse(out_path).getroot()
        for item in root.iter("def"):
            name.append(Def(item.findtext('line'),
                            item.findtext('type'),
                            item.findtext('name')))
        for item in root.iter("ref"):
            name.append(Ref(item.findtext('line'),
                            item.findtext('type'),
                            item.findtext('name'),
                            item.findtext('refLine')))
        return name


class Ref:
    def __init__(self, line, type, name, refLine):
        self.line = line
        self.type = type
        self.name = name
        self.refLine = refLine
        self.passed = False

    def __str__(self):
        return "Def(line={0}, type={1},name={2}, refLine={3})".format(self.line, self.type, self.name, self.refLine)

    def __eq__(self, other):
        if type(other) != Ref:
            return False
        return self.line == other.line and self.type == other.type and \
               self.name == other.name and self.refLine == other.refLine

    @property
    def status(self):
        return "correct" if self.passed else "incorrect"


class Def:
    def __init__(self, line, type, name):
        self.line = line
        self.type = type
        self.name = name
        self.passed = False

    def __str__(self):
        return "Def(line={0}, type={1},name={2})".format(self.line, self.type, self.name)

    def __eq__(self, other):
        if type(other) != Def:
            return False
        return self.line == other.line and self.type == other.type and self.name == other.name

    @property
    def status(self):
        return "correct" if self.passed else "incorrect"


class NameReport(BaseReport):

    def __init__(self, grade_result, gold_names, stu_names):
        self._grade = int(grade_result.count(True) / len(grade_result) * self.total_grade)
        self.gold_names = gold_names
        self.stu_names = stu_names
        self.creation_date = datetime.datetime.now()
        self.correct_num = grade_result.count(True)

    @property
    def report_name(self):
        return "name resolve"

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
        with open(os.path.join(Path(__file__).parent.absolute(), 'name_report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   grade=self.grade,
                                   total_grade=self.total_grade,
                                   stu_total=len(self.stu_names),
                                   gold_total=len(self.gold_names),
                                   correct_num=self.correct_num,
                                   units=self.stu_names)
