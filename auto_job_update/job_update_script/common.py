import os
import pathlib
import re
import shutil
import sys
import subprocess
import xml.etree.ElementTree as ET

G_JENKINS_CLI_ENV_USER_NAME = 'JENKINS_CLI_USER_NAME'
G_JENKINS_CLI_ENV_PASSWORD = 'JENKINS_CLI_PASSWORD'
G_JENKINS_CLI_JAR_NAME = 'jenkins-cli.jar'
G_OK = 0
G_ENV_DO_NOT_DEFINE = 1

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

    @property
    def jenkins_cli_jar_path(self):
        return self.__which(G_JENKINS_CLI_JAR_NAME)

    def __which(self, path: str) -> bool:
        return shutil.which(path)

    def __init__(self):
        self.__user_name = os.getenv(G_JENKINS_CLI_ENV_USER_NAME)
        self.__password = os.getenv(G_JENKINS_CLI_ENV_PASSWORD)

    def check(self) -> int:
        if (self.user_name == None or self.password == None):
            self.__dump_errors()
            return G_ENV_DO_NOT_DEFINE

        if not self.__is_pass_working(G_JENKINS_CLI_JAR_NAME):
            self.__dump_errors()
            return G_ENV_DO_NOT_DEFINE

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error("error: 以下環境変数を定義してから実行")
        self.__dump_error(f"  {G_JENKINS_CLI_ENV_USER_NAME}: jenkins-cli.jar 実行時のユーザー名")
        self.__dump_error(f"  {G_JENKINS_CLI_ENV_PASSWORD} : jenkins-cli.jar 実行時のパスワード or トークン")
        self.__dump_error(f"  jenkins-cli.jar に PATH を通す")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

    def __is_pass_working(self, path: str) -> bool:
        '''パスが通っているかを返す'''
        return self.__which(path) != None

class JobUrl:
    @property
    def full(self):
        return self.__full

    @property
    def master(self):
        return self.__master

    @property
    def relative_path(self):
        return self.__relative_path

    @property
    def job_name(self):
        return self.__job_name

    def __init__(self, job_url):
        self.__full = self.__remove_last_slash(job_url)
        self.__master = self.__get_master_url(self.__full)
        self.__relative_path = self.__get_job_relative_path(self.__full)
        self.__job_name = self.__get_job_name(self.__full)

    def __remove_last_slash(self, str_: str) -> str:
        '''末尾が "/" ならそれを削除'''
        res = re.sub(r"(.*)/$", r"\1", str_)
        return res

    def __get_master_url(self, full: str) -> str:
        '''
        in : http://localhost:8080/job/job_auto_update/job/build
        out: http://localhost:8080/
        '''
        return re.sub(r"(https?://[^/]+/).*", r"\1", full)

    def __get_job_relative_path(self, full: str) -> str:
        '''
        in : http://localhost:8080/job/job_auto_update/job/build
        out: job_auto_update/build
        '''
        # マスター部分(https?://localhost:8080/)以降の文字列取得
        tmp = re.sub(r"https?://[^/]+/(.*)", r"\1", full)

        # "job/" を全て削除
        return tmp.replace("job/", "")

    def __get_job_name(self, full: str) -> str:
        '''
        in : http://localhost:8080/job/job_auto_update/job/build
        out: build
        '''
        # 末尾がジョブ名
        return re.sub(r".*/([^/]+)", r"\1", full)

################################################################################
# 関数定義
################################################################################
def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

def execute_command(command: str) -> str:
    result = subprocess.run(command, shell=True)
    return result.returncode
