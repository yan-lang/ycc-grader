import datetime
import os

from jinja2 import Template
from pathlib import Path
from ..common.report import BaseReport


class AnalysisUnit:
    MISSING = 'missing'
    REDUNDANT = 'redundant'
    SIMILAR = 'similar'
    ERROR = 'error'
    CORRECT = 'correct'
    WARNING = 'warning'

    def __init__(self, status, stu_token, gold_token=None):
        self.status = status
        self.stu_token = stu_token
        self.gold_token = gold_token
        self.msgs = []

    def __str__(self):
        return self.status

    @staticmethod
    def similar(stu_token, gold_token):
        return AnalysisUnit(AnalysisUnit.SIMILAR, stu_token, gold_token)

    @staticmethod
    def missing(token):
        return AnalysisUnit(AnalysisUnit.MISSING, token)

    @staticmethod
    def redundant(token):
        return AnalysisUnit(AnalysisUnit.REDUNDANT, token)


class Message:
    WARNING = 'warning'
    ERROR = 'error'

    def __init__(self, msg, type):
        self.msg = msg
        self.type = type

    @staticmethod
    def warning(msg):
        return Message(msg, Message.WARNING)

    @staticmethod
    def error(msg):
        return Message(msg, Message.ERROR)

    def __str__(self):
        return self.type + ': ' + self.msg


class LexerReport(BaseReport):

    def __init__(self, file_name, stu_tokens, gold_tokens, analysis_result):
        self.analysis_result = analysis_result
        self.gold_tokens = gold_tokens
        self.stu_tokens = stu_tokens
        self.creation_date = datetime.datetime.now()
        self.file_name = file_name
        self.correct_num = 0
        self.error_num = 0
        self.redundant_num = 0
        self.missing_num = 0

        for unit in analysis_result:
            if unit.status == AnalysisUnit.CORRECT: self.correct_num += 1
            if unit.status == AnalysisUnit.ERROR: self.error_num += 1
            if unit.status == AnalysisUnit.REDUNDANT: self.redundant_num += 1
            if unit.status == AnalysisUnit.MISSING: self.missing_num += 1

    def render(self):
        with open(os.path.join(Path(__file__).parent.absolute(), 'report.html'), 'r') as f:
            template = Template(f.read(), lstrip_blocks=True, trim_blocks=True)
            return template.render(date=self.creation_date,
                                   file_name=self.file_name,
                                   stu_total=len(self.stu_tokens),
                                   gold_total=len(self.gold_tokens),
                                   correct_num=self.correct_num,
                                   error_num=self.error_num,
                                   redundant_num=self.redundant_num,
                                   missing_num=self.missing_num,
                                   units=self.analysis_result)

    @property
    def grade(self):
        return int(self.total_grade * (self.correct_num / len(self.stu_tokens)))

    @property
    def total_grade(self):
        return LexerReport.TOTAL_GRADE

    @property
    def report_name(self):
        return self.file_name

    @property
    def detail(self):
        return self.render()
