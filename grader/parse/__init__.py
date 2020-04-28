# coding=utf-8
"""
    语法分析自动评测脚本 v1.0

    - 脚本假设输入XML为正确格式
"""

import logging
import os

import untangle

from ..common import BaseRunner, BaseGrader
from ..common.report import ErrorReport
from ..common.util import load_json, check_extension

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Parser Grader")


class ParserRunner(BaseRunner):

    def get_output_dir_name(self):
        return "parse_out"

    def get_target(self):
        return "parse"

    def get_output_extension(self):
        return "xml"


class ParserGrader(BaseGrader):

    def get_runner(self) -> BaseRunner:
        return ParserRunner(logger)

    def grade_single(self, stu_out, gold_out):
        pass
