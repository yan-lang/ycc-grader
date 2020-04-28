import unittest

from grader.parse import ParserRunner, ParserGrader
import logging


class RunnerTestCase(unittest.TestCase):
    def test_run(self):
        runner = ParserRunner(logging.getLogger("test_parse"))
        runner.run('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar',
                   test_code_dir='../public/code/parse',
                   out_dir='../solution')


class ParserGraderTestCase(unittest.TestCase):
    def test_grade_single(self):
        grader = ParserGrader('', '')
        stu_xml = '../public/golden/parse/global_var.xml'
        gold_xml = '../solution/parse_out/global_var.xml'
        report = grader.grade_single(stu_xml, gold_xml)
        print(report.detail)


if __name__ == '__main__':
    unittest.main()
