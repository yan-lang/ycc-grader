# coding=utf-8
"""
    词法分析自动评测脚本 v1.0

    - 脚本假设输入XML为正确格式
"""
import json
import logging
import os
import subprocess

import untangle

from .lcs import lcs as compute_lcs
from .util import remove_extension, load_json
from .report import AnalysisUnit, LexerReport, Message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Lexer Grader")


class LexerRunner:
    """
    Runner负责执行程序并得到输出
    """

    def __init__(self, test_code_dir):
        # 测试文件文件路径
        self.test_cases = self._get_test_cases_(test_code_dir)

        # 构造运行命令
        self.runner = ['java']
        # self.runner.extend(['-Djava.security.manager'])
        # self.runner.extend(['-Djava.security.policy==myapp.policy'])
        self.runner.extend(['--enable-preview', '-jar'])

    def run(self, jar_path, out_dir):
        output_dir = os.path.join(out_dir, 'lex_out')
        os.makedirs(output_dir, exist_ok=True)

        for test_case in self.test_cases:
            logger.info('processing ' + test_case)
            base_name = remove_extension(os.path.basename(test_case))
            cmd = self.runner + [jar_path, test_case, '--target', 'lex', '-o',
                                 os.path.join(output_dir, base_name + '.xml')]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=False)
            stdout, stderr = p.communicate(timeout=100)
            status = {"return_code": p.returncode,
                      "stdout": stdout.decode(encoding="utf-8", errors="strict"),
                      "stderr": stderr.decode(encoding="utf-8", errors="strict")}
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


class LexerGrader:

    def __init__(self, test_code_dir, test_gold_dir):
        self.test_code_dir = test_code_dir
        self.test_gold_dir = test_gold_dir
        self.lexer_runner = LexerRunner(test_code_dir)

    def run(self, solution_path: str):
        """
        Grade a solution
        :param solution_path: the absolute path of the solution (.jar or .zip)
        :return: 
        """""
        if not solution_path.endswith(('.jar', '.zip')):
            raise ValueError('only jar and zip are accepted for grading')

        # Compiler if necessary

        # Run lexer to get output
        output_dir = os.path.dirname(solution_path)
        lex_out_dir = self.lexer_runner.run(solution_path, output_dir)

        # Grade output
        reports = []
        for out_name in os.listdir(self.test_gold_dir):
            if not out_name.endswith('.xml'):
                continue
            stu_out_path = os.path.join(lex_out_dir, out_name)
            gold_out_path = os.path.join(self.test_gold_dir, out_name)
            reports.append(self.grade_single(stu_out_path, gold_out_path))

        return reports

    @staticmethod
    def grade_single(stu_xml, gold_xml):
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