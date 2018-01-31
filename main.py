import argparse
import importlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute an arbitrary use case on multiple Docker containers')
    parser.add_argument('-u', '--usecase', type=str, dest='use_case', help='The use case to execute')
    args = parser.parse_args()
    if args.use_case:
        use_case_module = importlib.import_module('usecases.{}'.format(args.use_case))
        use_case_class = getattr(use_case_module, 'UseCase')
        if not use_case_class:
            print("Use case '{}' not found".format(args.use_case))
            exit(1)

        use_case_class.run()
