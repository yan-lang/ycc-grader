import unittest

from grader.parse import Runner, ParserGrader
import logging


class RunnerTestCase(unittest.TestCase):
    def test_run(self):
        runner = Runner(target='parse', output_dir='parse_out', output_extension='xml', logger=logging.getLogger('test'))
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

    def test_all(self):
        grader = ParserGrader('../public/code/parse', '../public/golden/parse')
        reports = grader.grade('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar')
        for report in reports:
            print(report.detail)

if __name__ == '__main__':
    unittest.main()
