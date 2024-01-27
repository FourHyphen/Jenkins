import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import *

import common

################################################################################
# usage:
#   引数:
#     基となるジョブ設定 xml パス
#     ジョブスクリプトパス
#     出力 xml ファイルパス
# ex:
#   python3 create_updating_job_xml.py './build.xml' './build_new.jenkinsfile' './build_new.xml'
################################################################################

################################################################################
# グローバル定数
################################################################################
G_OK = 0
G_ARGUMENT_ERROR = 1
G_FAIL_CREATE_XML = 2

################################################################################
# クラス定義
################################################################################
class CreateUpdatingJobXml:
    def __init__(self, base_xml_path: str, job_script_path: str, out_xml_path: str):
        self.__base_xml_path = base_xml_path
        self.__job_script_path = job_script_path
        self.__out_xml_path = out_xml_path

    def execute(self) -> int:
        # ベース xml 読み込み
        try:
            base_xml_root = read_xml(self.__base_xml_path)
        except Exception as e:
            common.dump_error(f'error: read_xml() failed: {self.__base_xml_path}')
            common.dump_error(e)
            return G_FAIL_CREATE_XML

        # ジョブスクリプト読み込み
        try:
            job_script_contents = read_file_utf_without_bom(self.__job_script_path)
        except Exception as e:
            common.dump_error(f'error: read_file_utf_without_bom() failed: {self.__job_script_path}')
            common.dump_error(e)
            return G_FAIL_CREATE_XML

        # ベース xml にジョブスクリプト部分を上書き
        try:
            update_job_contents(base_xml_root, job_script_contents)
        except Exception as e:
            common.dump_error(f'error: update_job_contents() failed')
            common.dump_error(e)
            return G_FAIL_CREATE_XML

        # ファイル保存
        try:
            save_xml(base_xml_root, self.__out_xml_path)
        except Exception as e:
            common.dump_error(f'error: save_xml() failed')
            common.dump_error(e)
            return G_FAIL_CREATE_XML

        return G_OK

################################################################################
# 関数定義
################################################################################
def read_xml(xml_path: str):
    '''return xml.etree.ElementTree.Element'''
    return ET.parse(xml_path).getroot()

def read_file_utf_without_bom(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf_8_sig') as f:
        return f.read()

def update_job_contents(base_xml_root, job_script_contents: str) -> None:
    if is_job_pipeline(base_xml_root):
        update_job_contents_pipeline(base_xml_root, job_script_contents)
    else:
        update_job_contents_freestyle(base_xml_root, job_script_contents)

def is_job_pipeline(base_xml_root) -> bool:
    return base_xml_root.find('definition') != None

def update_job_contents_pipeline(base_xml_root, job_script_contents: str) -> None:
    # <?xml version='1.1' encoding='UTF-8'?>
    # <flow-definition plugin="workflow-job@1186.v8def1a_5f3944">
    #   ...
    #   <definition>
    #     <script>ここがジョブスクリプト</script>
    for i in base_xml_root.find('definition'):
        if i.tag == 'script':
            i.text = job_script_contents
            return

    raise Exception('pipeline xml does not have "<definition><script>"')

def update_job_contents_freestyle(base_xml_root, job_script_contents: str) -> None:
    # <?xml version='1.1' encoding='UTF-8'?>
    # <project>
    #   <builders>
    #     <hudson.tasks.Shell>
    #       <command>ここがスクリプト</command>
    for builders in base_xml_root.find('builders'):
        for elem in builders:
            if elem.tag == 'command':
                elem.text = job_script_contents

    raise Exception('freestyle xml does not have "<builders><command>" or "<builders><scriptText>"')

def save_xml(xml_root, out_xml_path: str) -> None:
    # write 時の xml エスケープで '" はそのまま残る、このまま jenkins-cli.jar に通して OK
    # (get-job でダウンロードするときは html エスケープされた結果が保存されるので '" は html エスケープされている)
    # (このため get-job で DL した xml とは '" で差分が出る)
    tree = ET.ElementTree(xml_root)
    tree.write(out_xml_path, encoding='utf-8', method='xml')

################################################################################
# main 処理
################################################################################
def execute(args: list) -> int:
    res = check_args(args)
    if res != 0:
        return res

    return CreateUpdatingJobXml(args[1], args[2], args[3]).execute()

def check_args(args: list) -> int:
    if len(args) != 4:
        dump_args_error(args[0])
        return G_ARGUMENT_ERROR

    # 基となる xml が存在するかチェック
    if not os.path.exists(args[1]):
        common.dump_error(f'error: {args[1]} は存在しません')
        return G_ARGUMENT_ERROR

    # ジョブスクリプトが存在するかチェック
    if not os.path.exists(args[2]):
        common.dump_error(f'error: {args[2]} は存在しません')
        return G_ARGUMENT_ERROR

    return G_OK

def dump_args_error(arg0) -> None:
    common.dump_error('error: 引数は以下指定')
    common.dump_error('  引数1: 基となるジョブ設定 xml パス')
    common.dump_error('  引数2: ジョブスクリプトパス')
    common.dump_error('  引数3: 出力 xml ファイルパス')
    common.dump_error(f"  ex) python3 {arg0} './build.xml' './build_new.jenkinsfile' './build_new.xml'")

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(execute(args))
