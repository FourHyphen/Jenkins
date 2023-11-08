import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET
from common import JobUrl

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#   引数:
#     xml をダウンロードするジョブの URL
#     保存する xml ファイルパス
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 download_job_xml.py 'http://localhost:8080/job/job_auto_update/build' './build.xml'
################################################################################

################################################################################
# グローバル定数
################################################################################
G_JENKINS_CLI_JAR_PATH = '/work/jenkins-cli.jar'
G_JENKINS_CLI_ENV_USER_NAME = 'JENKINS_CLI_USER_NAME'
G_JENKINS_CLI_ENV_PASSWORD = 'JENKINS_CLI_PASSWORD'

G_OK = 0
G_ENV_DO_NOT_DEFINE = 1
G_ARGUMENT_ERROR = 2
G_DIRECTRY_DO_NOT_EXIST = 3
G_XML_GET_FAIL = 4
G_XML_DOWNLOADED_IS_NOT_XML = 5

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
    def job_url(self):
        return self.__job_url

    @property
    def save_xml_path(self):
        return self.__save_xml_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 3:
            self.__job_url = self.__args[1]
            self.__save_xml_path = self.__args[2]

    def check(self) -> int:
        if len(self.__args) != 3:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第一引数が URL 形式か、先頭 4 文字チェック
        if self.__args[1][0:4] != 'http':
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第二引数のディレクトリが存在するかチェック
        dir_path = os.path.dirname(self.__args[2])
        if not os.path.exists(dir_path):
            self.__dump_error(f"error: 保存先ディレクトリ '{dir_path}' は存在しません")
            return G_DIRECTRY_DO_NOT_EXIST

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 引数は以下指定")
        self.__dump_error("  引数1: xml をダウンロードするジョブの URL(http 始まり)")
        self.__dump_error("  引数2: 保存する xml ファイルパス(すでに存在するディレクトリを指定すること)")
        self.__dump_error(f"  ex) python3 {self.__args[0]} 'http://localhost:8080/job/job_auto_update/build' './build.xml'")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

class OutXmlPath:
    @property
    def path(self):
        return self.__path

    def __init__(self, app_args: AppArgs, job_url: JobUrl):
        self.__path = self.__create_path(app_args, job_url)

    def __create_path(self, app_args: AppArgs, job_url: JobUrl) -> str:
        return self.__to_abs_path(app_args.save_xml_path)

    def __to_abs_path(self, path: str) -> str:
        # resolve() の戻り値は PosixPath クラス
        return str(pathlib.Path(path).resolve())

################################################################################
# main 処理
################################################################################
def main(args:list) -> int:
    # 環境変数設定
    app_env = AppEnv()
    res = app_env.check()
    if res != 0:
        return res

    # 引数設定
    app_args = AppArgs(args)
    res = app_args.check()
    if res != 0:
        return res

    # xml ダウンロード
    return download_job_xml(app_env, app_args)

def download_job_xml(app_env: AppEnv, app_args: AppArgs):
    job_url = JobUrl(app_args.job_url)
    out_xml_path = OutXmlPath(app_args, job_url)

    # xml 取得コマンド作成
    command = create_command_download_job_xml(app_env, job_url, out_xml_path)

    # xml 取得
    if execute_command(command) != 0:
        dump_error("xml 取得コマンドの実行に失敗")
        return G_XML_GET_FAIL

    # 取得した xml が本当に xml 形式か確認
    if not is_file_xml(out_xml_path.path):
        dump_error("取得したファイルは xml ではありません")
        return G_XML_DOWNLOADED_IS_NOT_XML

    return G_OK

def create_command_download_job_xml(app_env: AppEnv, job_url: JobUrl, out_xml_path: OutXmlPath) -> str:
    print(f"java -jar {G_JENKINS_CLI_JAR_PATH} -s {job_url.master} -auth ****:**** get-job {job_url.relative_path} > {out_xml_path.path}")
    return f"java -jar {G_JENKINS_CLI_JAR_PATH} -s {job_url.master} -auth {app_env.user_name}:{app_env.password} get-job {job_url.relative_path} > {out_xml_path.path}"

def execute_command(command: str) -> str:
    result = subprocess.run(command, shell=True)
    return result.returncode

def is_file_xml(out_xml_path: str) -> bool:
    try:
        tree = ET.parse(out_xml_path)
        root = tree.getroot()
        return True
    except Exception as e:
        dump_error("xml downloaded is not xml.")
        dump_error(e)
        return False

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))
