import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

import download_job_xml
import create_updating_job_xml
import update_job_by_updating_xml
import common

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
G_ARGUMENT_ERROR = 2

################################################################################
# クラス定義
################################################################################
class UpdateJob:
    def __init__(self, job_url: str, job_script_path: str, update_xml_dir_path: str):
        self.__job_url = common.JobUrl(job_url)
        self.__job_script_path = job_script_path
        self.__update_xml_dir_path = update_xml_dir_path

    def execute(self) -> int:
        # 環境変数確認
        app_env = common.AppEnv()
        res = app_env.check()
        if res != 0:
            return res

        # ジョブ xml をダウンロード
        download_xml_path = create_download_xml_path(self.__update_xml_dir_path, self.__job_url.job_name)
        res = execute_download_job_xml(self.__job_url.full, download_xml_path)
        if res != 0:
            common.dump_error(f"download_job_xml return {res}")
            return res

        # 更新用 ジョブ xml を作成
        updating_xml_path = create_updating_xml_path(download_xml_path, self.__job_url.job_name)
        res = execute_create_updating_job_xml(download_xml_path, self.__job_script_path, updating_xml_path)
        if res != 0:
            common.dump_error(f"create_updating_job_xml return {res}")
            return res

        # 更新用 ジョブ xml を Jenkins ジョブに登録
        res = execute_update_job_by_updating_xml(self.__job_url.full, updating_xml_path)
        if res != 0:
            common.dump_error(f"update_job_by_updating_xml return {res}")
            return res

        return G_OK

################################################################################
# 関数定義
################################################################################
def create_download_xml_path(save_dir_path: str, job_name: str) -> str:
    return f"{save_dir_path}/{job_name}.xml"

def execute_download_job_xml(job_url: str, save_xml_path: str) -> int:
    return download_job_xml.execute(["download_job_xml.py", job_url, save_xml_path])

def create_updating_xml_path(download_xml_path: str, job_name: str) -> str:
    dir_path = os.path.dirname(download_xml_path)
    return f"{dir_path}/{job_name}_new.xml"

def execute_create_updating_job_xml(download_xml_path: str, job_script_path: str, updating_xml_path: str) -> int:
    return create_updating_job_xml.execute(["create_updating_job_xml.py", download_xml_path, job_script_path, updating_xml_path])

def execute_update_job_by_updating_xml(job_url: str, updating_xml_path: str) -> int:
    return update_job_by_updating_xml.execute(["update_job_by_updating_xml.py", job_url, updating_xml_path])

################################################################################
# main 処理
################################################################################
def execute(args: list) -> int:
    res = check_args(args)
    if res != 0:
        return res

    return UpdateJob(args[1], args[2], args[3]).execute()

def check_args(args: list) -> int:
    if len(args) != 4:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第一引数が URL 形式か、先頭 4 文字チェック
    if args[1][0:4] != 'http':
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第二引数のファイルが存在するかチェック
    if not os.path.exists(args[2]):
        common.dump_error(f"error: {args[2]} は存在しません")
        return G_ARGUMENT_ERROR

    # 第三引数のディレクトリが存在するかチェック
    if not os.path.exists(args[3]):
        common.dump_error(f"error: {args[3]} は存在しません")
        return G_ARGUMENT_ERROR

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error("error: 引数は以下指定")
    common.dump_error("  引数1: 更新するジョブの URL(http 始まり)")
    common.dump_error("  引数2: ジョブスクリプトファイルパス")
    common.dump_error("  引数3: Jenkins ジョブに上書き登録する xml の保存先ディレクトリパス")
    common.dump_error(f"  ex) python3 {arg0} 'http://localhost:8080/job/job_auto_update/build' '../script/build.jenkinsfile' './'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(execute(sys.argv))
