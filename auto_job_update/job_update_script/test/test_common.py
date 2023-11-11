import os
import pathlib
import sys
import unittest

G_TEST_DATA_ROOT = "./test/test_data/common"

# 作業ディレクトリ設定(常にこの py の 1 階層上にする)
dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(dir_path)

# テスト対象を load
sys.path.append(dir_path)    # PYTHONPATH に追加して初めて同階層以外の py を読める
import common

class TestMain(unittest.TestCase):
    def setUp(self):
        '''Init'''
        pass

    def tearDown(self):
        '''Clean'''
        pass

    def test_success_create_job_url_when_url_with_port(self):
        '''
        ジョブ URL がポート番号付きの場合に JobUrl クラスインスタンス化に成功する
        '''
        url = "http://localhost:8080/job/job_auto_update/job/build"
        job_url = common.JobUrl(url)

        self.assertEqual(url, job_url.full)
        self.assertEqual("http://localhost:8080/", job_url.master)
        self.assertEqual("job_auto_update/build", job_url.relative_path)
        self.assertEqual("build", job_url.job_name)

    def test_success_create_job_url_when_url_no_port(self):
        '''
        ジョブ URL がポート番号なしの場合に JobUrl クラスインスタンス化に成功する
        '''
        url = "http://localhost/job/job_auto_update/job/build"
        job_url = common.JobUrl(url)

        self.assertEqual(url, job_url.full)
        self.assertEqual("http://localhost/", job_url.master)
        self.assertEqual("job_auto_update/build", job_url.relative_path)
        self.assertEqual("build", job_url.job_name)

if __name__ == '__main__':
    unittest.main()
