import datetime
import json
import os
import re
import sys

from argparse import ArgumentParser
from enum import Enum

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
    ReadOnly = 1
    Update = 2
    Copy = 3
    All = 4
    Unknown = 5

class JobInfo:
    def __init__(self,
                 job_dir_url: str,
                 job_name: str,
                 job_script_dir_path: str,
                 save_updating_xml_dir_path: str):
        self.job_url = common.JobUrl(f'{job_dir_url}/{job_name}')

        # 更新に使用するジョブスクリプトファイルパス
        self.job_script_path = self.__get_job_script_path(job_script_dir_path, job_name)

        # 更新するジョブの現在の設定 xml 保存先パス
        self.download_xml_path = self.__create_download_xml_path(save_updating_xml_dir_path, job_name)

        # 更新に使用する xml パス
        self.updating_xml_path = self.__create_updating_xml_path(self.download_xml_path, job_name)

    def __get_job_script_path(self, job_script_dir_path: str, job_name: str) -> str:
        '''
        ディレクトリ内のジョブ名に相当するスクリプトファイルのパスを返す
        ジョブ名に相当するファイルがなければ空文字を返す
        '''
        for file_name in os.listdir(job_script_dir_path):
            if job_name in file_name:
                job_script_path = os.path.join(job_script_dir_path, file_name)
                if self.__is_extension_job_script(job_script_path):
                    return job_script_path

        print(f"Nothing job_name script(job_name = {job_name})\n")
        return ""

    def __is_extension_job_script(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[-1]
        return ext in [".java", ".jenkinsfile", ".groovy"]

    def __create_download_xml_path(self, update_xml_dir_path: str, job_name: str) -> str:
        return f"{update_xml_dir_path}/{job_name}.xml"

    def __create_updating_xml_path(self, download_xml_path: str, job_name: str) -> str:
        dir_path = os.path.dirname(download_xml_path)
        return f"{dir_path}/{job_name}_new.xml"

    def download_and_create_updating_xml(self) -> int:
        '''
        指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新するための xml を生成する
        ジョブスクリプトはジョブ名に相当するファイルから取得する
        '''
        # 更新に使用するジョブスクリプトファイルがなければスキップ
        if self.job_script_path == "":
            return 0

        # ジョブ xml をダウンロード
        res = self.__execute_download_job_xml(self.job_url.full, self.download_xml_path)
        if res != 0:
            common.dump_error(f"download_job_xml return {res}")
            return res

        # 更新用 ジョブ xml を作成
        res = self.__execute_create_updating_job_xml(self.download_xml_path, self.job_script_path, self.updating_xml_path)
        if res != 0:
            common.dump_error(f"create_updating_job_xml return {res}")
            return res

        return G_OK

    def __execute_download_job_xml(self, job_url: str, save_xml_path: str) -> int:
        return download_job_xml.execute(["download_job_xml.py", job_url, save_xml_path])

    def __execute_create_updating_job_xml(self, download_xml_path: str, job_script_path: str, updating_xml_path: str) -> int:
        return create_updating_job_xml.execute(["create_updating_job_xml.py", download_xml_path, job_script_path, updating_xml_path])

    def update(self) -> int:
        '''
        指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新する
        出力として更新に使用する xml ファイルを残す
        '''
        # 更新に使用するジョブスクリプトファイルがなければスキップ
        if self.job_script_path == "":
            return 0

        # ジョブ xml のダウンロードと更新用ジョブ xml 作成
        res = self.download_and_create_updating_xml()
        if res != 0:
            return res

        # 更新用 ジョブ xml を Jenkins ジョブに登録
        res = self.__execute_update_job_by_updating_xml(self.job_url.full, self.updating_xml_path)
        if res != 0:
            common.dump_error(f"update_job_by_updating_xml return {res}")
            return res

        return G_OK

    def __execute_update_job_by_updating_xml(self, job_url: str, updating_xml_path: str) -> int:
        return update_job_by_updating_xml.execute(["update_job_by_updating_xml.py", job_url, updating_xml_path])

    def copy(self) -> int:
        pass

    def all(self) -> int:
        pass

class EditJob:
    def __init__(self, json_path: str, execute_mode: ExecuteMode):
        self.__get_json_data(json_path)
        self.__execute_mode = execute_mode

    def __get_json_data(self, json_path: str) -> None:
        with open(json_path , 'r') as f:
            json_contents = json.load(f)

        self.__job_dir_urls = json_contents['job_dir_urls']
        self.__job_names = json_contents['job_names']
        self.__job_script_dir_path = json_contents['job_script_dir_path']
        self.__update_xml_dir_root_path = json_contents['update_xml_dir_root_path']

    def execute(self) -> int:
        # 環境変数確認
        res = common.AppEnv().check()
        if res != 0:
            return G_ENV_ERROR

        # 全ベース URL の全ジョブを更新
        date = get_now_date()
        result = 0
        for job_dir_url in self.__job_dir_urls:
            print(f"# update: {job_dir_url}")

            # 更新に使用する xml 保存先ディレクトリを作成
            save_updating_xml_dir_path = create_save_updating_xml_dir_path(self.__update_xml_dir_root_path, date, job_dir_url)
            os.makedirs(save_updating_xml_dir_path, exist_ok=True)

            # 当該ベース URL の全ジョブを更新
            for job_name in self.__job_names:
                job_info = JobInfo(job_dir_url=job_dir_url,
                                   job_name=job_name,
                                   job_script_dir_path=self.__job_script_dir_path,
                                   save_updating_xml_dir_path=save_updating_xml_dir_path)

                job_result = 1
                if self.__execute_mode == ExecuteMode.ReadOnly:
                    print(f"only read and create xml(not update).\n")
                    job_result = job_info.download_and_create_updating_xml()
                elif self.__execute_mode == ExecuteMode.Update:
                    job_result = job_info.update()

                if job_result != 0:
                    common.dump_error(f"error: {job_dir_url}, job name: {job_name}")
                    result = job_result
                print("")

            print("")

        return result

################################################################################
# 関数定義
################################################################################
def get_now_date() -> str:
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def create_save_updating_xml_dir_path(update_xml_dir_root_path: str, date: str, job_dir_url: str) -> str:
    '''更新に使用する xml を保存するディレクトリパスを作成する'''
    # ジョブ URL 文字列をディレクトリ名とする(ディレクトリ名に使えない文字を "_" で置換)
    job_unique = re.sub (r'[:/\.]', "_", job_dir_url)

    return f'{update_xml_dir_root_path}/{date}/{job_unique}'

################################################################################
# 引数＆オプション 処理
################################################################################
def get_option():
    parser = ArgumentParser()
    parser.add_argument('-r', '--readonly',
                        action='store_true',    # 本オプションが与えられたら True
                        help='If define, not update(read and create xml for update).')
    parser.add_argument('-u', '--update',
                        action='store_true',
                        help='If define, update(read and create xml for update and update by xml).')
    parser.add_argument('-c', '--copy',
                        action='store_true',
                        help='If define, copy(copy folder src to dst).')
    parser.add_argument('-a', '--all',
                        action='store_true',
                        help='If define, all(copy folder and read and update(dst)).')
    parser.add_argument('pos', nargs='*')
    return parser.parse_args()

def get_execute_mode(options) -> ExecuteMode:
    true_options = [option for option in [options.readonly, options.update, options.copy, options.all] if option]
    if len(true_options) != 1:
        return ExecuteMode.Unknown

    if options.readonly:
        return ExecuteMode.ReadOnly
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
        print("Please define -r or -u or -c or -a (only one).")
        exit(G_OPTIONS_ERROR)

    # 引数確認
    args.pos.insert(0, sys.argv[0])
    if check_args(args.pos) != 0:
        exit(G_ARGUMENT_ERROR)

    # 実行
    exit(EditJob(args.pos[1], execute_mode).execute())
