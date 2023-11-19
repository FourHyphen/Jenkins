import datetime
import json
import os
import re
import sys

from argparse import ArgumentParser
from enum import Enum

import copy_job
import download_job_xml
import create_updating_job_xml
import update_job_by_updating_xml
import common

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#     jenkins-cli.jar に PATH が通っていること
#   引数:
#     ジョブ設定を記載した json ファイルパス
#   機能
#     json の通りにジョブをコピー／更新する
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 edit_job.py "./input.json"
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
#     // ジョブ更新に使用する xml ファイルを保存するディレクトリパス
#     "update_xml_dir_root_path": "./__pycache__/save_xml"
# }
################################################################################

################################################################################
# グローバル定数: 固定
################################################################################
G_OK = 0
G_ENV_ERROR = 11
G_ARGUMENT_ERROR = 12
G_OPTIONS_ERROR = 13

################################################################################
# クラス定義
################################################################################
class ExecuteMode(Enum):
    DownloadAndCreateXml = 1
    Update = 2
    Copy = 3
    All = 4
    Unknown = 5

class JsonInfo:
    def __init__(self, json_path: str):
        self.__get_json_data(json_path)

    def __get_json_data(self, json_path: str) -> None:
        with open(json_path , 'r') as f:
            json_contents = json.load(f)

        self.job_update_urls          = self.__get_value_or_none(json_contents, 'job_update_urls')
        self.copy_urls                = self.__get_value_or_none(json_contents, 'copy_urls')
        self.job_names                = self.__get_value_or_none(json_contents, 'job_names')
        self.job_script_dir_path      = self.__get_value_or_none(json_contents, 'job_script_dir_path')
        self.update_xml_dir_root_path = self.__get_value_or_none(json_contents, 'update_xml_dir_root_path')

    def __get_value_or_none(self, dict, key: str):
        return dict[key] if key in dict else None

class ProcessCopy:
    def __init__(self, json_info: JsonInfo):
        self.__json_info = json_info

    def execute(self) -> int:
        result = 0

        for elem in self.__json_info.copy_urls:
            src, dst = elem['src'], elem['dst']
            print(f"# copy: {src} to {dst}")
            url_result = execute_copy_job(src, dst)
            if url_result != 0:
                result = url_result

        return result

class ProcessDownloadAndCreateXml:
    def __init__(self, json_info: JsonInfo):
        self.__json_info = json_info

    def execute(self) -> int:
        # 全ベース URL の全ジョブを更新
        date = get_now_date()
        result = 0
        for job_dir_url in self.__json_info.job_update_urls:
            print(f"# download and create xml: {job_dir_url}")

            # 更新に使用する xml 保存先ディレクトリを作成
            save_updating_xml_dir_path = create_save_updating_xml_dir_path(self.__json_info.update_xml_dir_root_path, date, job_dir_url)
            os.makedirs(save_updating_xml_dir_path, exist_ok=True)

            # 当該ベース URL の全ジョブをダウンロードして更新用 xml 生成
            for job_name in self.__json_info.job_names:
                job_url = common.JobUrl(f'{job_dir_url}/{job_name}')

                # 更新に使用するジョブスクリプトファイルパス
                job_script_path = get_job_script_path(self.__json_info.job_script_dir_path, job_name)

                # 更新するジョブの現在の設定 xml 保存先パス
                download_xml_path = create_download_xml_path(save_updating_xml_dir_path, job_name)

                # ダウンロード後 xml から生成する更新用 xml パス
                creating_xml_path = create_updating_xml_path(download_xml_path, job_name)

                job_result = download_and_create_updating_xml(job_url, job_script_path, download_xml_path, creating_xml_path)

                if job_result != 0:
                    common.dump_error(f"error: {job_dir_url}, job name: {job_name}")
                    result = job_result
                print("")

            print("")

        return result

class ProcessUpdate:
    def __init__(self, json_info: JsonInfo):
        self.__json_info = json_info

    def execute(self) -> int:
        # 全ベース URL の全ジョブを更新
        date = get_now_date()
        result = 0
        for job_dir_url in self.__json_info.job_update_urls:
            print(f"# update: {job_dir_url}")

            # 更新に使用する xml 保存先ディレクトリを作成
            save_updating_xml_dir_path = create_save_updating_xml_dir_path(self.__json_info.update_xml_dir_root_path, date, job_dir_url)
            os.makedirs(save_updating_xml_dir_path, exist_ok=True)

            # 当該ベース URL の全ジョブを更新
            for job_name in self.__json_info.job_names:
                job_result = update_job(job_dir_url, self.__json_info.job_script_dir_path, job_name, save_updating_xml_dir_path)

                if job_result != 0:
                    common.dump_error(f"error: {job_dir_url}, job name: {job_name}")
                    result = job_result
                print("")

            print("")

        return result

class ProcessAll:
    def __init__(self, json_info: JsonInfo):
        self.__json_info = json_info

    def execute(self) -> int:
        # 全 src URL を dst URL にコピー後、dst 内の全ジョブを更新
        date = get_now_date()
        result = 0

        for elem in self.__json_info.copy_urls:
            src, dst = elem['src'], elem['dst']
            print(f"# copy: {src} to {dst}")
            url_result = execute_copy_job(src, dst)
            if url_result != 0:
                result = url_result
                continue

            print(f"# update: {dst}")

            # 更新に使用する xml 保存先ディレクトリを作成
            save_updating_xml_dir_path = create_save_updating_xml_dir_path(self.__json_info.update_xml_dir_root_path, date, dst)
            os.makedirs(save_updating_xml_dir_path, exist_ok=True)

            # 当該 dst URL の全ジョブを更新
            for job_name in self.__json_info.job_names:
                job_result = update_job(dst, self.__json_info.job_script_dir_path, job_name, save_updating_xml_dir_path)

                if job_result != 0:
                    common.dump_error(f"error: {dst}, job name: {job_name}")
                    result = job_result
                print("")

            print("")

        return result

class EditJob:
    def __init__(self, json_path: str, execute_mode: ExecuteMode):
        self.__json_info = JsonInfo(json_path)
        self.__execute_mode = execute_mode

    def execute(self) -> int:
        # 環境変数確認
        res = common.AppEnv().check()
        if res != 0:
            return G_ENV_ERROR

        # モードに見合ったクラス名取得
        process = self.__get_process_class(self.__execute_mode)

        # 実行
        return process(self.__json_info).execute()

    def __get_process_class(self, execute_mode: ExecuteMode):
        '''
        in : 実行モード
        out: クラス(JsonInfo を引数とするイニシャライザを持ち、execute() メソッドを持つこと)
        '''
        if self.__execute_mode == ExecuteMode.Copy:
            return ProcessCopy
        elif self.__execute_mode == ExecuteMode.Update:
            return ProcessUpdate
        elif self.__execute_mode == ExecuteMode.DownloadAndCreateXml:
            return ProcessDownloadAndCreateXml
        elif self.__execute_mode == ExecuteMode.All:
            return ProcessAll
        else:
            raise("Execute mode is unknown.")

################################################################################
# 関数定義
################################################################################
def execute_copy_job(src_job_url: str, dst_job_url: str) -> int:
    return copy_job.execute(["copy_job.py", src_job_url, dst_job_url])

def get_now_date() -> str:
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def create_save_updating_xml_dir_path(update_xml_dir_root_path: str, date: str, job_dir_url: str) -> str:
    '''更新に使用する xml を保存するディレクトリパスを作成する'''
    # ジョブ URL 文字列をディレクトリ名とする(ディレクトリ名に使えない文字を "_" で置換)
    job_unique = re.sub (r'[:/\.]', "_", job_dir_url)

    return f'{update_xml_dir_root_path}/{date}/{job_unique}'

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

    print(f"Nothing job_name script(job_name = {job_name})\n")
    return ""

def is_extension_job_script(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[-1]
    return ext in [".java", ".jenkinsfile", ".groovy"]

def create_download_xml_path(update_xml_dir_path: str, job_name: str) -> str:
    return f"{update_xml_dir_path}/{job_name}.xml"

def download_and_create_updating_xml(job_url: common.JobUrl, job_script_path: str, download_xml_path: str, create_xml_path: str) -> int:
    '''
    指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新するための xml を生成する
    ジョブスクリプトはジョブ名に相当するファイルから取得する
    '''
    # 更新に使用するジョブスクリプトファイルがなければスキップ
    if job_script_path == "":
        return 0

    # ジョブ xml をダウンロード
    res = execute_download_job_xml(job_url.full, download_xml_path)
    if res != 0:
        common.dump_error(f"download_job_xml return {res}")
        return res

    # 更新用 ジョブ xml を作成
    res = execute_create_updating_job_xml(download_xml_path, job_script_path, create_xml_path)
    if res != 0:
        common.dump_error(f"create_updating_job_xml return {res}")
        return res

    return G_OK

def create_updating_xml_path(download_xml_path: str, job_name: str) -> str:
    dir_path = os.path.dirname(download_xml_path)
    return f"{dir_path}/{job_name}_new.xml"

def execute_download_job_xml(job_url: str, save_xml_path: str) -> int:
    return download_job_xml.execute(["download_job_xml.py", job_url, save_xml_path])

def execute_create_updating_job_xml(download_xml_path: str, job_script_path: str, updating_xml_path: str) -> int:
    return create_updating_job_xml.execute(["create_updating_job_xml.py", download_xml_path, job_script_path, updating_xml_path])

def update_job(job_dir_url, job_script_dir_path, job_name, save_updating_xml_dir_path) -> int:
    '''
    指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新する
    出力として更新に使用する xml ファイルを残す
    '''
    job_url = common.JobUrl(f'{job_dir_url}/{job_name}')

    # 更新に使用するジョブスクリプトファイルパス
    job_script_path = get_job_script_path(job_script_dir_path, job_name)

    # 更新するジョブの現在の設定 xml 保存先パス
    download_xml_path = create_download_xml_path(save_updating_xml_dir_path, job_name)

    # 更新に使用する xml パス
    updating_xml_path = create_updating_xml_path(download_xml_path, job_name)

    # 更新に使用するジョブスクリプトファイルがなければスキップ
    if job_script_path == "":
        return G_OK

    # ジョブ xml のダウンロードと更新用ジョブ xml 作成
    res = download_and_create_updating_xml(job_url, job_script_path, download_xml_path, updating_xml_path)
    if res != 0:
        return res

    # 更新用 ジョブ xml を Jenkins ジョブに登録
    res = execute_update_job_by_updating_xml(job_url.full, updating_xml_path)
    if res != 0:
        common.dump_error(f"update_job_by_updating_xml return {res}")
        return res

    return G_OK

def execute_update_job_by_updating_xml(job_url: str, updating_xml_path: str) -> int:
    return update_job_by_updating_xml.execute(["update_job_by_updating_xml.py", job_url, updating_xml_path])

################################################################################
# 引数＆オプション 処理
################################################################################
def get_option():
    parser = ArgumentParser()
    parser.add_argument('-dc', '--download_and_create_xml',
                        action='store_true',    # 本オプションが与えられたら True
                        help='If define, download and create xml for update.')
    parser.add_argument('-u', '--update',
                        action='store_true',
                        help='If define, update(download and create xml for update and update by xml).')
    parser.add_argument('-c', '--copy',
                        action='store_true',
                        help='If define, copy(copy folder src to dst).')
    parser.add_argument('-a', '--all',
                        action='store_true',
                        help='If define, all(copy folder and download and create xml and update(dst)).')
    parser.add_argument('pos', nargs='*')
    return parser.parse_args()

def get_execute_mode(options) -> ExecuteMode:
    true_options = [option for option in [options.download_and_create_xml, options.update, options.copy, options.all] if option]
    if len(true_options) != 1:
        return ExecuteMode.Unknown

    if options.download_and_create_xml:
        return ExecuteMode.DownloadAndCreateXml
    elif options.update:
        return ExecuteMode.Update
    elif options.copy:
        return ExecuteMode.Copy
    elif options.all:
        return ExecuteMode.All
    else:
        return ExecuteMode.Unknown

def check_args(args) -> int:
    if len(args) != 2:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # json が存在するかチェック
    if not os.path.exists(args[1]):
        common.dump_error(f"error: {args[1]} は存在しません")
        return G_ARGUMENT_ERROR

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error("error: 引数は以下指定")
    common.dump_error("  引数1: 各種設定を記載した json ファイルパス")
    common.dump_error(f"  ex) python3 {arg0} './input.json'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    args = get_option()

    # オプション確認
    execute_mode = get_execute_mode(args)
    if execute_mode == ExecuteMode.Unknown:
        print("Please define -dc or -u or -c or -a (only one).")
        exit(G_OPTIONS_ERROR)

    # 引数確認
    args.pos.insert(0, sys.argv[0])
    if check_args(args.pos) != 0:
        exit(G_ARGUMENT_ERROR)

    # 実行
    exit(EditJob(args.pos[1], execute_mode).execute())
