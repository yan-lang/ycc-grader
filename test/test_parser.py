import unittest

from grader.parse import ParserRunner
import logging


class RunnerTestCase(unittest.TestCase):
    def test_run(self):
        runner = ParserRunner('../public/code/parse', logging.getLogger("test_parse"))
        runner.run('../solution/yan-ycc-impl-1.0-SNAPSHOT-jar-with-dependencies.jar', '../solution')


if __name__ == '__main__':
    unittest.main()
