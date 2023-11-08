import os
import pathlib
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

################################################################################
# クラス定義
################################################################################
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
        self.__full = job_url
        self.__master = self.__get_master_url()
        self.__relative_path = self.__get_job_relative_path()
        self.__job_name = self.__get_job_name()

    def __get_master_url(self) -> str:
        '''
        in : http://localhost:8080/job/job_auto_update/job/build/
        out: http://localhost:8080/
        '''
        return re.sub(r"(https?://[^/]+/).*", r"\1", self.full)

    def __get_job_relative_path(self) -> str:
        '''
        in : http://localhost:8080/job/job_auto_update/job/build/
        out: job_auto_update/build
        '''
        # マスター部分を除外
        tmp = re.sub(r"https?://[^/]+/(.*)", r"\1", self.full)

        # "job/" を全て削除
        return tmp.replace("job/", "")

    def __get_job_name(self) -> str:
        # 最後が "/" ならそれを削除
        tmp = self.__remove_last_slash(self.full)

        # 末尾がジョブ名
        return re.sub(r".*/([^/]+)", r"\1", tmp)

    def __remove_last_slash(self, str_: str) -> str:
        res = re.sub(r"(.*)/$", r"\1", str_)
        return res
