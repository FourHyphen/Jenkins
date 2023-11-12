import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import *

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
class AppArgs:
    @property
    def base_xml_path(self):
        return self.__base_xml_path

    @property
    def job_script_path(self):
        return self.__job_script_path

    @property
    def out_xml_path(self):
        return self.__out_xml_path

    def __init__(self, args):
        self.__args = args
        if len(self.__args) == 4:
            self.__base_xml_path = self.__args[1]
            self.__job_script_path = self.__args[2]
            self.__out_xml_path = self.__args[3]

    def check(self) -> int:
        if len(self.__args) != 4:
            self.__dump_errors()
            return G_ARGUMENT_ERROR

        # 基となる xml が存在するかチェック
        if not os.path.exists(self.__base_xml_path):
            self.__dump_error(f'error: {self.__base_xml_path} は存在しません')
            return G_ARGUMENT_ERROR

        # ジョブスクリプトが存在するかチェック
        if not os.path.exists(self.__job_script_path):
            self.__dump_error(f'error: {self.__job_script_path} は存在しません')
            return G_ARGUMENT_ERROR

        return G_OK

    def __dump_errors(self) -> None:
        self.__dump_error('error: 引数は以下指定')
        self.__dump_error('  引数1: 基となるジョブ設定 xml パス')
        self.__dump_error('  引数2: ジョブスクリプトパス')
        self.__dump_error('  引数3: 出力 xml ファイルパス')
        self.__dump_error(f"  ex) python3 {self.__args[0]} './build.xml' './build_new.jenkinsfile' './build_new.xml'")

    def __dump_error(self, str_: str) -> None:
        print(str_, file=sys.stderr)

################################################################################
# main 処理
################################################################################
def main(args:list) -> int:
    # 引数設定
    app_args = AppArgs(args)
    res = app_args.check()
    if res != 0:
        return res

    # xml 作成
    return create_updating_job_xml(app_args)

def create_updating_job_xml(app_args: AppArgs) -> int:
    # ベース xml 読み込み
    try:
        base_xml_root = read_xml(app_args.base_xml_path)
    except Exception as e:
        dump_error(f'error: read_xml() failed: {app_args.base_xml_path}')
        dump_error(e)
        return G_FAIL_CREATE_XML

    # ジョブスクリプト読み込み
    try:
        job_script_contents = read_file_utf_without_bom(app_args.job_script_path)
    except Exception as e:
        dump_error(f'error: read_file_utf_without_bom() failed: {app_args.job_script_path}')
        dump_error(e)
        return G_FAIL_CREATE_XML

    # ベース xml にジョブスクリプト部分を上書き
    try:
        update_job_contents(base_xml_root, job_script_contents)
    except Exception as e:
        dump_error(f'error: update_job_contents() failed')
        dump_error(e)
        return G_FAIL_CREATE_XML

    # ファイル保存
    try:
        save_xml(base_xml_root, app_args.out_xml_path)
    except Exception as e:
        dump_error(f'error: save_xml() failed')
        dump_error(e)
        return G_FAIL_CREATE_XML

    return G_OK

def read_xml(xml_path: str):
    '''return xml.etree.ElementTree.Element'''
    return ET.parse(xml_path).getroot()

def dump_error(str_: str) -> None:
    print(str_, file=sys.stderr)

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

def save_xml(xml_root, out_xml_path: str) -> None:
    # write 時の xml エスケープで '" はそのまま残る、このまま jenkins-cli.jar に通して OK
    # (get-job でダウンロードするときは html エスケープされた結果が保存されるので '" は html エスケープされている)
    # (このため get-job で DL した xml とは '" で差分が出る)
    tree = ET.ElementTree(xml_root)
    tree.write(out_xml_path, encoding='utf-8', method='xml')

################################################################################
# スクリプトとして実行された場合のみ main 処理を実行
################################################################################
if __name__ == '__main__':
    exit(main(sys.argv))
