import datetime
import json
import os
import re
import sys

from argparse import ArgumentParser

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

################################################################################
# クラス定義
################################################################################
class UpdateJobAll:
    def __init__(self, json_path: str, do_only_read: bool):
        self.__get_json_data(json_path)
        self.__do_only_read = do_only_read
        if self.__do_only_read:
            print(f"only read and create xml(not update).\n")

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

            # 更新に使用した xml 保存先ディレクトリを作成
            update_xml_dir_path = create_update_xml_dir_path(self.__update_xml_dir_root_path, date, job_dir_url)
            os.makedirs(update_xml_dir_path, exist_ok=True)

            # 当該ベース URL の全ジョブを更新
            for job_name in self.__job_names:
                job_result = self.update_job(self.__job_script_dir_path, job_dir_url, job_name, update_xml_dir_path)
                if job_result != 0:
                    common.dump_error(f"update error: {job_dir_url}, job name: {job_name}")
                    result = job_result
                print("")

            print("")

        return result

    def update_job(self, job_script_dir_path: str, job_dir_url: str, job_name: str, update_xml_dir_path: str) -> int:
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

        job_url = common.JobUrl(f'{job_dir_url}/{job_name}')

        # 環境変数確認
        app_env = common.AppEnv()
        res = app_env.check()
        if res != 0:
            return res

        # ジョブ xml をダウンロード
        download_xml_path = self.create_download_xml_path(update_xml_dir_path, job_url.job_name)
        res = self.execute_download_job_xml(job_url.full, download_xml_path)
        if res != 0:
            common.dump_error(f"download_job_xml return {res}")
            return res

        # 更新用 ジョブ xml を作成
        updating_xml_path = self.create_updating_xml_path(download_xml_path, job_url.job_name)
        res = self.execute_create_updating_job_xml(download_xml_path, job_script_path, updating_xml_path)
        if res != 0:
            common.dump_error(f"create_updating_job_xml return {res}")
            return res

        if self.__do_only_read:
            print(f"read only, not update.")
        else:
            # 更新用 ジョブ xml を Jenkins ジョブに登録
            res = self.execute_update_job_by_updating_xml(job_url.full, updating_xml_path)
            if res != 0:
                common.dump_error(f"update_job_by_updating_xml return {res}")
                return res

        return G_OK

    def create_download_xml_path(self, save_dir_path: str, job_name: str) -> str:
        return f"{save_dir_path}/{job_name}.xml"

    def execute_download_job_xml(self, job_url: str, save_xml_path: str) -> int:
        return download_job_xml.execute(["download_job_xml.py", job_url, save_xml_path])

    def create_updating_xml_path(self, download_xml_path: str, job_name: str) -> str:
        dir_path = os.path.dirname(download_xml_path)
        return f"{dir_path}/{job_name}_new.xml"

    def execute_create_updating_job_xml(self, download_xml_path: str, job_script_path: str, updating_xml_path: str) -> int:
        return create_updating_job_xml.execute(["create_updating_job_xml.py", download_xml_path, job_script_path, updating_xml_path])

    def execute_update_job_by_updating_xml(self, job_url: str, updating_xml_path: str) -> int:
        return update_job_by_updating_xml.execute(["update_job_by_updating_xml.py", job_url, updating_xml_path])


################################################################################
# 関数定義
################################################################################
def get_now_date() -> str:
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def create_update_xml_dir_path(update_xml_dir_root_path: str, date: str, job_dir_url: str) -> str:
    '''更新に使用した xml を保存するディレクトリパスを作成する'''
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

    return ""

def is_extension_job_script(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[-1]
    return ext in [".java", ".jenkinsfile", ".groovy"]


################################################################################
# main 処理
################################################################################
def get_option():
    parser = ArgumentParser()
    parser.add_argument('-r', '--readonly',
                        action='store_true',    # 本オプションが与えられたら True
                        help='If define, not update(read and create xml for update).')
    parser.add_argument('pos', nargs='*')
    return parser.parse_args()

def execute(args: list, do_only_read: bool) -> int:
    res = check_args(args)
    if res != 0:
        return res

    return UpdateJobAll(args[1], do_only_read).execute()

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
    args.pos.insert(0, sys.argv[0])
    exit(execute(args.pos, args.readonly))
