# coding=utf-8
"""
    词法分析自动评测脚本 v1.0

    - 脚本假设输入XML为正确格式
"""
import logging
import os

import untangle

from .report import AnalysisUnit, LexerReport, Message
from ..common import BaseRunner, BaseGrader
from ..common.lcs import lcs as compute_lcs

logging.basicConfig(level   =logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Lexer Grader")


class LexerRunner(BaseRunner):

    def get_output_dir_name(self):
        return "lex_out"

    def get_target(self):
        return "lex"

    def get_output_extension(self):
        return "xml"


class LexerGrader(BaseGrader):

    def get_runner(self) -> BaseRunner:
        return LexerRunner(logger)

    def grade_single(self, stu_xml, gold_xml):
        """ 给一个文件打分

        :param stu_xml: 学生输出xml文件的内容
        :param gold_xml: 标准输出xml文件的内容
        :return:
        """
        stu_tokens = untangle.parse(stu_xml).tokens.token
        gold_tokens = untangle.parse(gold_xml).tokens.token
        rough_result = LexerGrader._rough_cmp(stu_tokens, gold_tokens)
        for unit in rough_result:
            if unit.status == AnalysisUnit.SIMILAR:
                LexerGrader._analyze_similar(unit)
        report = LexerReport(os.path.basename(gold_xml),
                             stu_tokens,
                             gold_tokens,
                             rough_result)
        return report

    @staticmethod
    def _rough_cmp(stu_tokens, gold_tokens):
        lcs = compute_lcs(stu_tokens, gold_tokens, lambda x, y: x.type == y.type)
        stu_idxes, gold_idxes = [], []
        for stu_idx, gold_idx in lcs:
            stu_idxes.append(stu_idx)
            gold_idxes.append(gold_idx)
        result = []
        i, j, k = 0, 0, 0
        while k < len(lcs):
            while i < stu_idxes[k]:
                result.append(AnalysisUnit.redundant(stu_tokens[i]))
                i += 1
            while j < gold_idxes[k]:
                result.append(AnalysisUnit.missing(gold_tokens[j]))
                j += 1
            result.append(AnalysisUnit.similar(stu_tokens[i], gold_tokens[j]))
            i += 1
            j += 1
            k += 1

        # 有可能出现这种情况
        # stu:  1,2,3,4
        # gold: 1,2,4,3,5,6
        # 最后一组similar是stu[2]和gold[3], 因此还需要遍历stu_tokens和gold_tokens把剩下的加上
        while i < len(stu_idxes):
            result.append(AnalysisUnit.redundant(stu_tokens[i]))
            i += 1
        while j < len(gold_idxes):
            result.append(AnalysisUnit.missing(gold_tokens[j]))
            j += 1

        return result

    @staticmethod
    def _analyze_similar(analysis_unit):
        """
        Similar unit has the same type, so we only need to compare
        source, value, line, column, start, stop
        """
        stu_token = analysis_unit.stu_token
        gold_token = analysis_unit.gold_token

        msgs = []
        warning_num = 0
        error_num = 0

        def cmp_property(stu, gold, name, msg_factory):
            if stu != gold:
                msgs.append(msg_factory("expect {0}={1}, got {0}={2}".format(name, gold.cdata, stu.cdata)))
                return 1
            return 0

        warning_num += cmp_property(stu_token.source, gold_token.source, 'source', Message.warning)
        error_num += cmp_property(stu_token.value, gold_token.value, 'value', Message.error)
        error_num += cmp_property(stu_token.line, gold_token.line, 'line', Message.error)
        error_num += cmp_property(stu_token.column, gold_token.column, 'column', Message.error)
        error_num += cmp_property(stu_token.start, gold_token.start, 'start', Message.error)
        error_num += cmp_property(stu_token.stop, gold_token.stop, 'stop', Message.error)

        analysis_unit.msgs.extend(msgs)
        if error_num > 0:
            analysis_unit.status = AnalysisUnit.ERROR
        elif warning_num > 0:
            analysis_unit.status = AnalysisUnit.WARNING
        else:
            analysis_unit.status = AnalysisUnit.CORRECT
