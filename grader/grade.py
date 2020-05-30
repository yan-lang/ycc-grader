import argparse

from lex import LexerGrader

parser = argparse.ArgumentParser()
parser.add_argument("--code", required=True, help="The test code")
parser.add_argument("--gold", required=True, help="The golden solution of test code")
parser.add_argument("jar", help="The jar of your solution")

if __name__ == '__main__':
    args = parser.parse_args()

    grader = LexerGrader(args.code, args.gold)
    reports = grader.run(args.jar)
    for report in reports:
        print(report.render())
