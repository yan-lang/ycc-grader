import unittest

from grader.ir import IRGrader


class MyTestCase(unittest.TestCase):
    def test_something(self):
        grader = IRGrader('../public/code/ir', '../public/golden/ir')
        reports = grader.grade('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies-good.jar')
        for report in reports:
            print(report.detail)


if __name__ == '__main__':
    unittest.main()
