import unittest

import untangle

from grader.lex import LexerGrader, LexerRunner
from grader.common.lcs import lcs


class RunnerTestCase(unittest.TestCase):
    def test_run(self):
        runner = LexerRunner('../public/code/lexer')
        runner.run('../solution/yan.ycc.impl-1.0-SNAPSHOT-jar-with-dependencies.jar', '../solution/out')


class XMLTestCase(unittest.TestCase):
    def test_object(self):
        stu_xml = open('../solution/lex_out/float_literal.xml')
        stu_tokens = untangle.parse(stu_xml).tokens.token
        print(stu_tokens[0].value.cdata)


class LexerTestCase(unittest.TestCase):
    def test_grade_single(self):
        stu_xml = '../solution/lex_out/float_literal.xml'
        gold_xml = '../public/golden/lexer/float_literal.xml'
        result = LexerGrader.grade_single(stu_xml, gold_xml)
        print(result.render())

    def test_run(self):
        grader = LexerGrader('../public/code/lexer', '../public/golden/lexer')
        reports = grader.run('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies-bad.jar')
        for report in reports:
            print(report.detail)


class LCSTestCase(unittest.TestCase):
    def test_lcs1(self):
        a = [1, 2, 3, 4, 5, 6, 7]
        b = [1, 0, 2, 4, 3, 4, 7, 5, 6, 7]
        result = lcs(a, b)
        self.assertEqual([(0, 0), (1, 2), (2, 4), (3, 5), (4, 7), (5, 8), (6, 9)], result)

    def test_lcs2(self):
        a = [1, 2, 3, 4, 5, 6, 7]
        b = [1, 0, 2, 4, 3, 4, 7, 5, 6]
        result = lcs(a, b)
        self.assertEqual([(0, 0), (1, 2), (2, 4), (3, 5), (4, 7), (5, 8)], result)


if __name__ == '__main__':
    unittest.main()
