import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

import common

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
class UpdateJobByUpdatingXml:
    def __init__(self, job_url: str, xml_path: str):
        self.__job_url = common.JobUrl(job_url)
        self.__xml_path = xml_path

    def execute(self) -> int:
        # 環境変数設定
        app_env = common.AppEnv()
        res = app_env.check()
        if res != 0:
            return G_ENV_ERROR

        # ジョブ更新コマンド作成
        command = self.create_command_update_job(app_env)

        # ジョブ更新
        if common.execute_command(command) != 0:
            common.dump_error("ジョブ更新コマンドの実行に失敗")
            return G_JOB_UPDATE_FAIL

        return G_OK

    def create_command_update_job(self, app_env: common.AppEnv) -> str:
        print(f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__job_url.master} -auth ****:**** update-job {self.__job_url.relative_path} < {self.__xml_path}")
        return f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__job_url.master} -auth {app_env.user_name}:{app_env.password} update-job {self.__job_url.relative_path} < {self.__xml_path}"

################################################################################
# main 処理
################################################################################
def execute(args: list) -> int:
    res = check_args(args)
    if res != 0:
        return(res)

    return UpdateJobByUpdatingXml(args[1], args[2]).execute()

def check_args(args: list) -> int:
    if len(args) != 3:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第一引数が URL 形式か、先頭 4 文字チェック
    if args[1][0:4] != 'http':
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第二引数のファイルが存在するかチェック
    if not os.path.exists(args[2]):
        common.dump_error(f"error: {args[2]} は存在しません")
        return G_XML_DO_NOT_EXIST

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error("error: 引数は以下指定")
    common.dump_error("  引数1: 更新するジョブの URL(http 始まり)")
    common.dump_error("  引数2: xml ファイルパス")
    common.dump_error(f"  ex) python3 {arg0} 'http://localhost:8080/job/job_auto_update/build' '/work/git/update_job.xml'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    execute(sys.argv)
