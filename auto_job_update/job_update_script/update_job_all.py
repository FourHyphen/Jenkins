import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

import update_job

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#   引数:
#     ジョブスクリプトファイルが存在するディレクトリパス
#     ジョブ更新に使用した xml ファイルを保存するディレクトリパス
#   機能
#     全ジョブ URL ルートに存在する全ジョブを指定ジョブスクリプトディレクトリに存在する
#     ジョブスクリプトファイルで更新する
#     ジョブ更新に使用した xml ファイルを指定ディレクトリパスにジョブ URL ルート毎に保存する
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 update_job_all.py "./script" "./save_xml"
################################################################################

################################################################################
# グローバル定数: ユーザー設定項目
################################################################################
G_JOB_DIR_URLS = ['http://localhost:8080/job/job_auto_update',
                  'http://localhost:8080/job/job_auto_update2']
G_JOB_NAMES = ['build', 'seed_task']

################################################################################
# グローバル定数: 固定
################################################################################
G_JENKINS_CLI_ENV_USER_NAME = 'JENKINS_CLI_USER_NAME'
G_JENKINS_CLI_ENV_PASSWORD = 'JENKINS_CLI_PASSWORD'

G_OK = 0
G_ENV_DO_NOT_DEFINE = 1
G_ARGUMENT_ERROR = 2
G_DIR_DO_NOT_EXIST = 3

################################################################################
# クラス定義
################################################################################
class AppEnv:
    @property
    def user_name(self):
        return self.__user_name

    @property
    def password(self):
        return self.__password

    def __init__(self):
        self.__user_name = os.getenv(G_JENKINS_CLI_ENV_USER_NAME)
        self.__password = os.getenv(G_JENKINS_CLI_ENV_PASSWORD)

    def check(self) -> int:
        if (self.user_name == None or self.password == None):
            self.__dump_errors()
            return G_ENV_DO_NOT_DEFINE
        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 以下環境変数を定義してから実行")
        self.__dump_error(f"  {G_JENKINS_CLI_ENV_USER_NAME}: jenkins-cli.jar 実行時のユーザー名")
        self.__dump_error(f"  {G_JENKINS_CLI_ENV_PASSWORD} : jenkins-cli.jar 実行時のパスワード or トークン")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

class AppArgs:
    @property
    def job_script_dir_path(self):
        return self.__job_script_dir_path

    @property
    def update_xml_dir_root_path(self):
        return self.__update_xml_dir_root_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 3:
            self.__job_script_dir_path = self.__args[1]
            self.__update_xml_dir_root_path = self.__args[2]

    def check(self) -> int:
        if len(self.__args) != 3:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第一引数のディレクトリが存在するかチェック
        if not os.path.exists(self.__args[1]):
            self.__dump_error(f"error: {self.__args[1]} は存在しません")
            return G_DIR_DO_NOT_EXIST

        # 第二引数のディレクトリがない場合は作成するのでチェック不要
        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 引数は以下指定")
        self.__dump_error("  引数1: 更新するジョブのスクリプトファイルを入れたディレクトリパス")
        self.__dump_error("  引数2: ジョブ更新に使用した xml を保存するディレクトリパス")
        self.__dump_error(f"  ex) python3 {self.__args[0]} './job_script' './save_xml'")

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

    # 全ベース URL の全ジョブを更新
    result = 0
    for job_dir_url in G_JOB_DIR_URLS:
        print(f"# update: ${job_dir_url}")

        # 更新に使用した xml 保存先ディレクトリを作成
        update_xml_dir_path = create_update_xml_dir_path(app_args.update_xml_dir_root_path, job_dir_url)
        os.makedirs(update_xml_dir_path, exist_ok=True)

        # 当該ベース URL の全ジョブを更新
        for job_name in G_JOB_NAMES:
            job_result = update_job_core(app_args, job_dir_url, job_name, update_xml_dir_path)
            if job_result != 0:
                dump_error(f"update error: {job_dir_url}, job name: {job_name}")
                result = job_result

        print("")

    return result

def create_update_xml_dir_path(update_xml_dir_root_path: str, job_dir_url: str) -> str:
    '''更新に使用した xml を保存するディレクトリパスを作成する'''
    job_unique = re.sub (r'[:/\.]', "_", job_dir_url)
    return f'{update_xml_dir_root_path}/{job_unique}'

def update_job_core(app_args: AppArgs, job_dir_url: str, job_name: str, update_xml_dir_path: str) -> int:
    '''
    指定ジョブ URL の指定ジョブ名のジョブスクリプトを更新する
    ジョブスクリプトはジョブ名に相当するファイルから取得する
    出力として更新に使用した xml ファイルを残す
    '''
    # 更新に使用するジョブスクリプトファイルパスを特定
    job_script_path = get_job_script_path(app_args.job_script_dir_path, job_name)
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
    file_names = os.listdir(job_script_dir_path)

    for file_name in file_names:
        if job_name in file_name:
            job_script_path = os.path.join(job_script_dir_path, file_name)
            if is_extension_job_script(job_script_path):
                return job_script_path

    return ""

def is_extension_job_script(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[-1]
    return ext in [".java", ".jenkinsfile", ".groovy"]

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))
