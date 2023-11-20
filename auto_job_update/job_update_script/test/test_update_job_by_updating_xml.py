import os
import pathlib
import sys
import unittest

G_TEST_DATA_ROOT = "./test_data/update_job_by_updating_xml"

# 作業ディレクトリ設定(常にこの py の階層にする)
# dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)
sys.path.append(dir_path)    # PYTHONPATH に追加して初めて同階層以外の py を読める

# テスト対象を load(テスト対象は 1 階層上)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_job_by_updating_xml

class TestMain(unittest.TestCase):
    def setUp(self):
        '''Init'''
        pass

    def tearDown(self):
        '''Clean'''
        pass

    def test_args_error_when_args_len_less_than_2(self):
        '''
        引数が 2 つ未満なら return 2
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("sys.argv[1]")
        args.append("sys.argv[2]")

        res = update_job_by_updating_xml.check_args(args)

        self.assertEqual(2, res)

    def test_args_error_when_1st_arg_not_http(self):
        '''
        第一引数が http 始まりでないなら return 2
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("not_http")
        args.append(os.path.join(G_TEST_DATA_ROOT, "xml.xml"))

        res = update_job_by_updating_xml.check_args(args)

        self.assertEqual(2, res)

    def test_args_error_when_directory_do_not_exist(self):
        '''
        第二引数のファイルが存在しないなら return 3
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("http://localhost:8080")
        args.append(os.path.join(G_TEST_DATA_ROOT, "not_exist_file.xml"))

        res = update_job_by_updating_xml.check_args(args)

        self.assertEqual(3, res)

if __name__ == '__main__':
    unittest.main()
