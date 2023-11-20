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
G_OK = 0
G_ENV_ERROR = 1
G_ARGUMENT_ERROR = 2
G_DIRECTRY_DO_NOT_EXIST = 3
G_XML_GET_FAIL = 4
G_XML_DOWNLOADED_IS_NOT_XML = 5

################################################################################
# クラス定義
################################################################################
class DownloadJobXml:
    def __init__(self, job_url: str, out_xml_path: str):
        self.__job_url = common.JobUrl(job_url)
        self.__out_xml_path = self.__to_abs_path(out_xml_path)

    def __to_abs_path(self, path: str) -> str:
        # resolve() の戻り値は PosixPath クラス
        return str(pathlib.Path(path).resolve())

    ################################################################################
    # main 処理
    ################################################################################
    def execute(self) -> int:
        # 環境変数設定
        app_env = common.AppEnv()
        res = app_env.check()
        if res != 0:
            return G_ENV_ERROR

        # xml 取得コマンド作成
        command = self.__create_command_download_job_xml(app_env)

        # xml 取得
        if common.execute_command(command) != 0:
            common.dump_error("xml 取得コマンドの実行に失敗")
            return G_XML_GET_FAIL

        # 取得した xml が本当に xml 形式か確認
        if not is_file_xml(self.__out_xml_path):
            common.dump_error("取得したファイルは xml ではありません")
            return G_XML_DOWNLOADED_IS_NOT_XML

        return G_OK

    def __create_command_download_job_xml(self, app_env: common.AppEnv) -> str:
        print(f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__job_url.master} -auth ****:**** get-job {self.__job_url.relative_path} > {self.__out_xml_path}")
        return f"java -jar {app_env.jenkins_cli_jar_path} -s {self.__job_url.master} -auth {app_env.user_name}:{app_env.password} get-job {self.__job_url.relative_path} > {self.__out_xml_path}"

################################################################################
# 関数定義
################################################################################
def is_file_xml(out_xml_path: str) -> bool:
    try:
        tree = ET.parse(out_xml_path)
        root = tree.getroot()
        return True
    except Exception as e:
        common.dump_error("xml downloaded is not xml.")
        common.dump_error(e)
        return False

################################################################################
# main 処理
################################################################################
def execute(args: list) -> int:
    res = check_args(args)
    if res != 0:
        return res

    return DownloadJobXml(args[1], args[2]).execute()

def check_args(args: list) -> int:
    if len(args) != 3:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第一引数が URL 形式か、先頭 4 文字チェック
    if args[1][0:4] != 'http':
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 第二引数ファイルパスのディレクトリが存在するかチェック
    dir_path = os.path.dirname(args[2])
    if not os.path.exists(dir_path):
        common.dump_error(f"error: 保存先ディレクトリ '{dir_path}' は存在しません")
        dump_args_error(args[0])
        return G_DIRECTRY_DO_NOT_EXIST

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error("error: 引数は以下指定")
    common.dump_error("  引数1: xml をダウンロードするジョブの URL(http 始まり)")
    common.dump_error("  引数2: 保存する xml ファイルパス(すでに存在するディレクトリを指定すること)")
    common.dump_error(f"  ex) python3 {arg0} 'http://localhost:8080/job/job_auto_update/build' './build.xml'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(execute(sys.argv))
