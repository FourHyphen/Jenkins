import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

import download_job_xml
import create_updating_job_xml
import update_job_by_updating_xml
from common import AppEnv, JobUrl

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#   引数:
#     更新する Jenkins ジョブの URL
#     ジョブスクリプトパス
#     Jenkins ジョブに上書き登録する xml の保存先ディレクトリパス
#   機能
#     指定 URL ジョブを指定ジョブスクリプトファイルの中身で更新する
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 update_job.py 'http://localhost:8080/job/job_auto_update/build' '../script/build.jenkinsfile' './'
################################################################################

################################################################################
# グローバル定数
################################################################################
G_OK = 0
G_ENV_DO_NOT_DEFINE = 1
G_ARGUMENT_ERROR = 2

################################################################################
# クラス定義
################################################################################
class AppArgs:
    @property
    def job_url(self):
        return self.__job_url

    @property
    def job_script_path(self):
        return self.__job_script_path

    @property
    def update_xml_dir_path(self):
        return self.__update_xml_dir_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 4:
            self.__job_url = self.__args[1]
            self.__job_script_path = self.__args[2]
            self.__update_xml_dir_path = self.__args[3]

    def check(self) -> int:
        if len(self.__args) != 4:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第一引数が URL 形式か、先頭 4 文字チェック
        if self.__args[1][0:4] != 'http':
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第二引数のファイルが存在するかチェック
        if not os.path.exists(self.__args[2]):
            self.__dump_error(f"error: {self.__args[2]} は存在しません")
            return G_ARGUMENT_ERROR

        # 第三引数のディレクトリが存在するかチェック
        if not os.path.exists(self.__args[3]):
            self.__dump_error(f"error: {self.__args[3]} は存在しません")
            return G_ARGUMENT_ERROR

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 引数は以下指定")
        self.__dump_error("  引数1: 更新するジョブの URL(http 始まり)")
        self.__dump_error("  引数2: ジョブスクリプトファイルパス")
        self.__dump_error("  引数3: Jenkins ジョブに上書き登録する xml の保存先ディレクトリパス")
        self.__dump_error(f"  ex) python3 {self.__args[0]} 'http://localhost:8080/job/job_auto_update/build' '../script/build.jenkinsfile' './'")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

################################################################################
# main 処理
################################################################################
def main(args:list) -> int:
    # 環境変数確認
    app_env = AppEnv()
    res = app_env.check()
    if res != 0:
        return res

    # 引数設定
    app_args = AppArgs(args)
    res = app_args.check()
    if res != 0:
        return res

    # ジョブ更新
    return update_job(app_args)

def update_job(app_args: AppArgs) -> int:
    job_url = JobUrl(app_args.job_url)

    # ジョブ xml をダウンロード
    download_xml_path = create_download_xml_path(app_args.update_xml_dir_path, job_url.job_name)
    res = execute_download_job_xml(app_args.job_url, download_xml_path)
    if res != 0:
        dump_error(f"download_job_xml return {res}")
        return res

    # 更新用 ジョブ xml を作成
    updating_xml_path = create_updating_xml_path(download_xml_path, job_url.job_name)
    res = execute_create_updating_job_xml(download_xml_path, app_args.job_script_path, updating_xml_path)
    if res != 0:
        dump_error(f"create_updating_job_xml return {res}")
        return res

    # 更新用 ジョブ xml を Jenkins ジョブに登録
    res = execute_update_job_by_updating_xml(job_url.full, updating_xml_path)
    if res != 0:
        dump_error(f"update_job_by_updating_xml return {res}")
        return res

    return G_OK

def create_download_xml_path(save_dir_path: str, job_name: str) -> str:
    return f"{save_dir_path}/{job_name}.xml"

def execute_download_job_xml(job_url: str, save_xml_path: str) -> int:
    return download_job_xml.main(["download_job_xml.py", job_url, save_xml_path])

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

def create_updating_xml_path(download_xml_path: str, job_name: str) -> str:
    dir_path = os.path.dirname(download_xml_path)
    return f"{dir_path}/{job_name}_new.xml"

def execute_create_updating_job_xml(download_xml_path: str, job_script_path: str, updating_xml_path: str) -> int:
    args = ["create_updating_job_xml.py", download_xml_path, job_script_path, updating_xml_path]
    return create_updating_job_xml.main(args)

def execute_update_job_by_updating_xml(job_url: str, updating_xml_path: str) -> int:
    args = ["update_job_by_updating_xml.py", job_url, updating_xml_path]
    return update_job_by_updating_xml.main(args)

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))