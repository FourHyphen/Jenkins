import os
import pathlib
import re
import sys
import subprocess

import common

################################################################################
# usage:
#   環境変数:
#     JENKINS_CLI_USER_NAME: ユーザー名
#     JENKINS_CLI_PASSWORD : パスワード
#   引数:
#     ジョブ(フォルダも可)の URL(src)
#     ジョブ(フォルダも可)の URL(dst)
# ex:
#   export JENKINS_CLI_USER_NAME=admin
#   export JENKINS_CLI_PASSWORD=password
#   python3 copy_job.py 'http://localhost:8080/job/job_auto_update/build' 'http://localhost:8080/job/job_auto_update/build2'
################################################################################

################################################################################
# グローバル定数
################################################################################
G_OK = 0
G_ENV_ERROR = 1
G_ARGUMENT_ERROR = 2
G_COPY_ERROR = 3

################################################################################
# クラス定義
################################################################################
class CopyJob:
    def __init__(self, src_job_url: str, dst_job_url: str):
        self.__src_job_url = common.JobUrl(src_job_url)
        self.__dst_job_url = common.JobUrl(dst_job_url)

    ################################################################################
    # main 処理
    ################################################################################
    def execute(self) -> int:
        # 環境変数設定
        app_env = common.AppEnv()
        res = app_env.check()
        if res != 0:
            return G_ENV_ERROR

        # コピーコマンド作成
        command = self.__create_command_copy(app_env)

        # コピー
        if common.execute_command(command) != 0:
            common.dump_error("コピー失敗")
            return G_COPY_ERROR

        return G_OK

    def __create_command_copy(self, app_env: common.AppEnv) -> str:
        print(f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__src_job_url.master} -auth ****:**** copy-job {self.__src_job_url.relative_path} {self.__dst_job_url.relative_path}")
        return f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__src_job_url.master} -auth {app_env.user_name}:{app_env.password} copy-job {self.__src_job_url.relative_path} {self.__dst_job_url.relative_path}"

################################################################################
# main 処理
################################################################################
def execute(args: list) -> int:
    res = check_args(args)
    if res != 0:
        return res

    return CopyJob(args[1], args[2]).execute()

def check_args(args: list) -> int:
    if len(args) != 3:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第一引数が URL 形式か、先頭 4 文字チェック
    if args[1][0:4] != 'http':
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第二引数が URL 形式か、先頭 4 文字チェック
    if args[2][0:4] != 'http':
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error("error: 引数は以下指定")
    common.dump_error("  引数1: ジョブ(フォルダも可)の URL(src)")
    common.dump_error("  引数2: ジョブ(フォルダも可)の URL(dst)")
    common.dump_error(f"  ex) python3 {arg0} 'http://localhost:8080/job/job_auto_update/build' 'http://localhost:8080/job/job_auto_update/build2'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(execute(sys.argv))
