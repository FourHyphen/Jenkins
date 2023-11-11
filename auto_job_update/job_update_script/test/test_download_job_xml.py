import os
import pathlib
import sys
import unittest

G_TEST_DATA_ROOT = "./test_data/download_job_xml"

# 作業ディレクトリ設定(常にこの py の階層にする)
# dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)
sys.path.append(dir_path)    # PYTHONPATH に追加して初めて同階層以外の py を読める

# テスト対象を load(テスト対象は 1 階層上)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import download_job_xml

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
        app_args = download_job_xml.AppArgs(args)

        res = app_args.check()
        self.assertEqual(2, res)

    def test_args_error_when_1st_arg_not_http(self):
        '''
        第一引数が http 始まりでないなら return 2
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("not_http")
        args.append(G_TEST_DATA_ROOT)
        app_args = download_job_xml.AppArgs(args)

        res = app_args.check()
        self.assertEqual(2, res)

    def test_args_error_when_directory_do_not_exist(self):
        '''
        第二引数指定のファイルのディレクトリが存在しないなら return 3
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("http://localhost:8080")
        args.append(os.path.join(G_TEST_DATA_ROOT, "not_exist_directory/save.xml"))
        app_args = download_job_xml.AppArgs(args)

        res = app_args.check()
        self.assertEqual(3, res)

    def test_success_create_out_xml_path(self):
        '''
        OutXmlPath クラスインスタンス化に成功する
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("http://localhost:8080")
        args.append(os.path.join(G_TEST_DATA_ROOT, "save.xml"))    # 存在するディレクトリへの出力設定にする
        app_args = download_job_xml.AppArgs(args)

        out_xml_path = download_job_xml.OutXmlPath(app_args)

        # 絶対パスを生成するため、末尾のファイル名のみ確認する
        self.assertEqual("save.xml", os.path.basename(out_xml_path.path))

    def test_is_file_xml(self):
        '''
        is_file_xml() は xml 形式のファイルの場合に True を返す
        '''
        # xml 形式の場合は True を返す
        path = os.path.join(G_TEST_DATA_ROOT, "xml.xml")
        self.assertTrue(os.path.exists(path))

        res = download_job_xml.is_file_xml(path)
        self.assertTrue(res)

        # xml 形式でないファイルの場合は False を返す
        path = os.path.join(G_TEST_DATA_ROOT, "not_xml.xml")
        self.assertTrue(os.path.exists(path))

        res = download_job_xml.is_file_xml(path)
        self.assertFalse(res)

if __name__ == '__main__':
    unittest.main()
