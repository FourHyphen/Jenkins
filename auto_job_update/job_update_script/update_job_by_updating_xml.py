import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET
from common import AppEnv, JobUrl

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#   引数:
#     更新するジョブの URL
#     xml ファイルパス
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 update_job_by_updating_xml.py 'http://localhost:8080/job/job_auto_update/build' './build.xml'
################################################################################

################################################################################
# グローバル定数
################################################################################
G_OK = 0
G_ENV_ERROR = 1
G_ARGUMENT_ERROR = 2
G_XML_DO_NOT_EXIST = 3
G_JOB_UPDATE_FAIL = 4

################################################################################
# クラス定義
################################################################################
class AppArgs:
    @property
    def job_url(self):
        return self.__job_url

    @property
    def xml_path(self):
        return self.__xml_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 3:
            self.__job_url = self.__args[1]
            self.__xml_path = self.__args[2]

    def check(self) -> int:
        if len(self.__args) != 3:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第一引数が URL 形式か、先頭 4 文字チェック
        if self.__args[1][0:4] != 'http':
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 第二引数のファイルが存在するかチェック
        if not os.path.exists(self.__args[2]):
            self.__dump_error(f"error: {self.__args[2]} は存在しません")
            return G_XML_DO_NOT_EXIST

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 引数は以下指定")
        self.__dump_error("  引数1: 更新するジョブの URL(http 始まり)")
        self.__dump_error("  引数2: xml ファイルパス")
        self.__dump_error(f"  ex) python3 {self.__args[0]} 'http://localhost:8080/job/job_auto_update/build' '/work/git/update_job.xml'")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

class XmlPath:
    @property
    def path(self):
        return self.__path

    def __init__(self, path: str):
        self.__path = path

################################################################################
# main 処理
################################################################################
def main(args:list) -> int:
    # 環境変数設定
    app_env = AppEnv()
    res = app_env.check()
    if res != 0:
        return G_ENV_ERROR

    # 引数設定
    app_args = AppArgs(args)
    res = app_args.check()
    if res != 0:
        return res

    # ジョブ更新
    return update_job(app_env, app_args)

def update_job(app_env: AppEnv, app_args: AppArgs):
    job_url = JobUrl(app_args.job_url)
    xml_path = XmlPath(app_args.xml_path)

    # ジョブ更新コマンド作成
    command = create_command_update_job(app_env, job_url, xml_path)

    # ジョブ更新
    if execute_command(command) != 0:
        dump_error("ジョブ更新コマンドの実行に失敗")
        return G_JOB_UPDATE_FAIL

    return G_OK

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

def create_command_update_job(app_env: AppEnv, job_url: JobUrl, xml_path: XmlPath) -> str:
    print(f"java -jar {app_env.jenkins_cli_jar_path} -s {job_url.master} -auth ****:**** update-job {job_url.relative_path} < {xml_path.path}")
    return f"java -jar {app_env.jenkins_cli_jar_path} -s {job_url.master} -auth {app_env.user_name}:{app_env.password} update-job {job_url.relative_path} < {xml_path.path}"

def execute_command(command: str) -> str:
    result = subprocess.run(command, shell=True)
    return result.returncode

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))
