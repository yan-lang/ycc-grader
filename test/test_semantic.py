import logging
import unittest

from grader.common import Runner
from grader.semantic.cs import ControlStructureGrader
from grader.semantic.name import NameResolveGrader


class MyTestCase(unittest.TestCase):
    def test_cs_run(self):
        runner = Runner(target='cs', output_dir='cs_out', output_extension='xml',
                        logger=logging.getLogger('test'))
        runner.run('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar',
                   test_code_dir='../public/code/semantic/cs',
                   out_dir='../solution')

    def test_name_run(self):
        runner = Runner(target='name', output_dir='name_out', output_extension='xml',
                        logger=logging.getLogger('test'))
        runner.run('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar',
                   test_code_dir='../public/code/semantic/name',
                   out_dir='../solution')

    def test_cs_grader(self):
        grader = ControlStructureGrader('../public/code/semantic/cs', '../public/golden/semantic/cs')
        reports = grader.grade('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar')
        for report in reports:
            print(report.detail)

    def test_name_grader(self):
        grader = NameResolveGrader('../public/code/semantic/name', '../public/golden/semantic/name')
        reports = grader.grade('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar')
        for report in reports:
            print(report.detail)


if __name__ == '__main__':
    unittest.main()
