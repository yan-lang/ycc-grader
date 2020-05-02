# coding=utf-8
"""
    语义分析自动评测脚本 v1.0
"""

import logging
import os

from grader.common import Grader
from grader.semantic.cs import ControlStructureGrader
from grader.semantic.name import NameResolveGrader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Semantic Grader")


class SemanticGrader(Grader):

    def __init__(self, test_code_dir, test_gold_dir):
        super().__init__(test_code_dir, test_gold_dir)
        self.cs_grader = ControlStructureGrader(os.path.join(test_code_dir, 'cs'), os.path.join(test_gold_dir, 'cs'))
        self.name_grader = NameResolveGrader(os.path.join(test_code_dir, 'name'), os.path.join(test_gold_dir, 'name'))

    def grade(self, submitted_file):
        reports = []
        reports += self.cs_grader.grade(submitted_file)
        reports += self.name_grader.grade(submitted_file)
        return reports
