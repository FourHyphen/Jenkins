import os
import sys
from unittest import TestLoader
from unittest import TextTestRunner

# 作業ディレクトリ設定(常にこの py の階層にする)
dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

def main():
    loader = TestLoader()
    test = loader.discover("./")
    runner = TextTestRunner()
    runner.run(test)

if __name__ == '__main__':
    main()
