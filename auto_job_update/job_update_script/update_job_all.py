import json
import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

import update_job
from common import AppEnv

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#     jenkins-cli.jar に PATH が通っていること
#   引数:
#     ジョブ設定を記載した json ファイルパス
#   機能
#     全ジョブ URL ルートに存在する全ジョブを指定ジョブスクリプトディレクトリに存在するジョブスクリプトファイルで更新する
#     ジョブ更新に使用した xml ファイルを指定ディレクトリパスにジョブ URL ルート毎に保存する
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 update_job_all.py "./input.json"
# json 例:
# {
#     "job_dir_urls": [
#         "http://localhost:8080/job/job_folder"
#     ],
#     "job_names": [
#         "job_name_a",
#         "job_name_b"
#     ],
#     // ジョブスクリプトファイルが存在するディレクトリパス
#     "job_script_dir_path"     : "./__pycache__/script",
#     // ジョブ更新に使用した xml ファイルを保存するディレクトリパス
#     "update_xml_dir_root_path": "./__pycache__/save_xml"
# }
################################################################################

################################################################################
# グローバル定数: 固定
################################################################################
G_OK = 0
G_ENV_ERROR = 1
G_ARGUMENT_ERROR = 2
G_JSON_ERROR = 3

################################################################################
# クラス定義
################################################################################
class AppArgs:
    @property
    def json_path(self):
        return self.__json_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 2:
            self.__json_path = self.__args[1]

    def check(self) -> int:
        if len(self.__args) != 2:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # json が存在するかチェック
        if not os.path.exists(self.json_path):
            self.__dump_error(f"error: {self.json_path} は存在しません")
            return G_ARGUMENT_ERROR

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 引数は以下指定")
        self.__dump_error("  引数1: 各種設定を記載した json ファイルパス")
        self.__dump_error(f"  ex) python3 {self.__args[0]} './input.json'")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

class AppJson:
    @property
    def job_dir_urls(self) -> list:
        return self.__job_dir_urls

    @property
    def job_names(self) -> list:
        return self.__job_names

    @property
    def job_script_dir_path(self) -> str:
        return self.__job_script_dir_path

    @property
    def update_xml_dir_root_path(self) -> str:
        return self.__update_xml_dir_root_path

    def __init__(self, json_path: str):
        self.__get_json_data(json_path)

    def __get_json_data(self, json_path: str) -> None:
        with open(json_path , 'r') as f:
            json_contents = json.load(f)

        self.__job_dir_urls = json_contents['job_dir_urls']
        self.__job_names = json_contents['job_names']
        self.__job_script_dir_path = json_contents['job_script_dir_path']
        self.__update_xml_dir_root_path = json_contents['update_xml_dir_root_path']

################################################################################
# main 処理
################################################################################
def main(args:list) -> int:
    # 環境変数確認
    res = AppEnv().check()
    if res != 0:
        return G_ENV_ERROR

    # 引数設定
    app_args = AppArgs(args)
    res = app_args.check()
    if res != 0:
        return res

    # 引数指定の json 解析
    try:
        app_json = AppJson(app_args.json_path)
    except Exception as e:
        dump_error(e)
        return G_JSON_ERROR

    # 全ベース URL の全ジョブを更新
    result = 0
    for job_dir_url in app_json.job_dir_urls:
        print(f"# update: {job_dir_url}")

        # 更新に使用した xml 保存先ディレクトリを作成
        update_xml_dir_path = create_update_xml_dir_path(app_json.update_xml_dir_root_path, job_dir_url)
        os.makedirs(update_xml_dir_path, exist_ok=True)

        # 当該ベース URL の全ジョブを更新
        for job_name in app_json.job_names:
            job_result = update_job_core(app_json.job_script_dir_path, job_dir_url, job_name, update_xml_dir_path)
            if job_result != 0:
                dump_error(f"update error: {job_dir_url}, job name: {job_name}")
                result = job_result
            print("")

        print("")

    return result

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

def create_update_xml_dir_path(update_xml_dir_root_path: str, job_dir_url: str) -> str:
    '''更新に使用した xml を保存するディレクトリパスを作成する'''
    # ジョブ URL 文字列をディレクトリ名とする(ディレクトリ名に使えない文字を "_" で置換)
    job_unique = re.sub (r'[:/\.]', "_", job_dir_url)

    return f'{update_xml_dir_root_path}/{job_unique}'

def update_job_core(job_script_dir_path: str, job_dir_url: str, job_name: str, update_xml_dir_path: str) -> int:
    '''
    指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新する
    ジョブスクリプトはジョブ名に相当するファイルから取得する
    出力として更新に使用した xml ファイルを残す
    '''
    # 更新に使用するジョブスクリプトファイルパスを特定
    job_script_path = get_job_script_path(job_script_dir_path, job_name)
    if job_script_path == "":
        print(f"Nothing job_name script(job_name = {job_name})")
        return 0

    args = ["update_job.py", f'{job_dir_url}/{job_name}', job_script_path, update_xml_dir_path]
    return update_job.main(args)

def get_job_script_path(job_script_dir_path: str, job_name: str) -> str:
    '''
    ディレクトリ内のジョブ名に相当するスクリプトファイルのパスを返す
    ジョブ名に相当するファイルがなければ空文字を返す
    '''
    for file_name in os.listdir(job_script_dir_path):
        if job_name in file_name:
            job_script_path = os.path.join(job_script_dir_path, file_name)
            if is_extension_job_script(job_script_path):
                return job_script_path

    return ""

def is_extension_job_script(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[-1]
    return ext in [".java", ".jenkinsfile", ".groovy"]

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))
