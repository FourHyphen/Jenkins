import os
import pathlib
import sys
import unittest

G_TEST_DATA_ROOT = "./test_data/create_updating_xml"

# 作業ディレクトリ設定(常にこの py の階層にする)
# dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)
sys.path.append(dir_path)    # PYTHONPATH に追加して初めて同階層以外の py を読める

# テスト対象を load(テスト対象は 1 階層上)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import create_updating_job_xml

class TestMain(unittest.TestCase):
    def setUp(self):
        '''Init'''
        pass

    def tearDown(self):
        '''Clean'''
        pass

    def test_args_error_when_args_len_less_than_3(self):
        '''
        引数が 3 つ未満なら return 1
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append("sys.argv[1]")
        args.append("sys.argv[2]")

        res = create_updating_job_xml.check_args(args)

        self.assertEqual(1, res)

    def test_args_error_when_xml_do_not_exist(self):
        '''
        第一引数の xml が存在しないなら return 1
        '''
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append(os.path.join(G_TEST_DATA_ROOT, "not_exist.xml"))
        args.append(os.path.join(G_TEST_DATA_ROOT, "xml.xml"))    # 第一引数確認のため存在するファイルを指定
        args.append("sys.argv[3]")

        res = create_updating_job_xml.check_args(args)

        self.assertEqual(1, res)

    def test_args_error_when_job_script_do_not_exist(self):
        '''
        第二引数のジョブスクリプトファイルが存在しないなら return 1
        '''
        base_xml_path = os.path.join(G_TEST_DATA_ROOT, "xml.xml")
        args = []
        args.append("sys.argv[0]")    # スクリプト名
        args.append(base_xml_path)
        self.assertTrue(os.path.exists(base_xml_path))
        args.append(os.path.join(G_TEST_DATA_ROOT, "not_exist.jenkinsfile"))
        args.append("sys.argv[3]")

        res = create_updating_job_xml.check_args(args)

        self.assertEqual(1, res)

    def test_read_xml(self):
        '''
        read_xml() は xml 形式ファイルの読み込みに成功する
        '''
        # xml 形式ファイルの場合は成功
        xml_path = os.path.join(G_TEST_DATA_ROOT, "xml.xml")
        res = create_updating_job_xml.read_xml(xml_path)
        self.assertTrue(res != None)

        # xml 形式でないファイルの場合は例外送出
        xml_path = os.path.join(G_TEST_DATA_ROOT, "not_xml.xml")
        with self.assertRaises(Exception):
            create_updating_job_xml.read_xml(xml_path)

    def test_success_read_job_script_when_utf_8_with_bom(self):
        '''
        UTF8 with BOM のジョブスクリプトファイル読み込みに成功する
        '''
        path = os.path.join(G_TEST_DATA_ROOT, "utf_8_bom.txt")
        res = create_updating_job_xml.read_file_utf_without_bom(path)
        self.assertEqual("utf-8 bom", res)

    def test_success_read_job_script_when_utf_8_no_bom(self):
        '''
        UTF8(BOM なし)のジョブスクリプトファイル読み込みに成功する
        '''
        path = os.path.join(G_TEST_DATA_ROOT, "utf_8_no_bom.txt")
        res = create_updating_job_xml.read_file_utf_without_bom(path)
        self.assertEqual("utf-8 no bom", res)

    def test_update_job_contents_pipeline(self):
        '''
        パイプラインジョブのベース xml の definition.script 階層に新規ジョブスクリプトを上書き設定する
        '''
        base_xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "base_xml_root.xml"))
        job_script = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "new_job_script.jenkinsfile"))

        create_updating_job_xml.update_job_contents(base_xml_root, job_script)

        for i in base_xml_root.find('definition'):
            if i.tag == 'script':
                self.assertEqual("import\n", i.text)

    def test_exception_if_job_contents_pipeline_do_not_exist_definition_script(self):
        '''
        パイプラインジョブのベース xml に definition.script 階層が存在しない場合に例外を送出する
        '''
        base_xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "base_xml_root_no_definition_script.xml"))
        job_script = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "new_job_script.jenkinsfile"))

        with self.assertRaises(Exception):
            create_updating_job_xml.update_job_contents(base_xml_root, job_script)

    def test_update_job_contents_freestyle_command(self):
        '''
        パイプラインジョブのベース xml の builders の下の command 階層に新規ジョブスクリプトを上書き設定する
        '''
        base_xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "freestyle_xml_root_command.xml"))
        job_script = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "new_job_script.jenkinsfile"))

        create_updating_job_xml.update_job_contents(base_xml_root, job_script)

        for builders in base_xml_root.find('builders'):
            for elem in builders:
                if elem.tag == 'command':
                    self.assertEqual("import\n", elem.text)

    def test_update_job_contents_freestyle_scriptText(self):
        '''
        パイプラインジョブのベース xml の builders の下の scriptText 階層に新規ジョブスクリプトを上書き設定する
        '''
        base_xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "freestyle_xml_root_scriptText.xml"))
        job_script = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "new_job_script.jenkinsfile"))

        create_updating_job_xml.update_job_contents(base_xml_root, job_script)

        for builders in base_xml_root.find('builders'):
            for elem in builders:
                if elem.tag == 'command':
                    self.assertEqual("import\n", elem.text)

    def test_exception_if_job_contents_freestyle_do_not_exist_command_or_scriptText(self):
        '''
        フリースタイルジョブのベース xml の builders 階層に command も scriptText も存在しない場合に例外を送出する
        '''
        base_xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "freestyle_xml_root_no_definition_command_or_scriptText.xml"))
        job_script = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "new_job_script.jenkinsfile"))

        with self.assertRaises(Exception):
            create_updating_job_xml.update_job_contents(base_xml_root, job_script)

    def test_save_xml(self):
        xml_root = create_updating_job_xml.read_xml(os.path.join(G_TEST_DATA_ROOT, "save.xml"))
        out_xml_path = os.path.join(G_TEST_DATA_ROOT, "save_actual.xml")

        # 準備: 出力がすでにある場合は削除
        if os.path.exists(out_xml_path):
            os.remove(out_xml_path)

        create_updating_job_xml.save_xml(xml_root, out_xml_path)
        expected_xml = create_updating_job_xml.read_file_utf_without_bom(os.path.join(G_TEST_DATA_ROOT, "save_expected.xml"))
        actual_xml = create_updating_job_xml.read_file_utf_without_bom(out_xml_path)

        self.assertEqual(expected_xml, actual_xml)

        # 成功した場合に限りここを通る: 後始末
        if os.path.exists(out_xml_path):
            os.remove(out_xml_path)

if __name__ == '__main__':
    unittest.main()

