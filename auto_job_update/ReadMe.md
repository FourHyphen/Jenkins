# 1. 概要
- 環境構築
  - イメージビルド
  - コンテナ起動
  - コンテナ内にジョブスクリプトファイルを配置
- スクリプト実行
  - 引数に指定したオプションと input.json の通りにジョブを更新したりする

# 2. 環境構築
## イメージビルド方法
```
cd <Dockerfile 置いたディレクトリ>
docker build -f ./Dockerfile -t update-jenkins-job:latest .
```

## コンテナ起動方法
コンテナ名に指定ありません。コンテナ名を変更したい場合は yml を編集してください。
```
cd <docker-compose yml 置いたディレクトリ>
docker-compose -f dc_update_jenkins_job.yml up -d
```

## 更新に使用するジョブスクリプトをコンテナから見える場所に配置
- パスはどこでも OK

# 3. in/out
全てコンテナ内

## in
- 環境変数
  - `JENKINS_CLI_USER_NAME`: Jenkins ユーザー名
  - `JENKINS_CLI_PASSWORD`: Jenkins ユーザーのパスワード or トークン文字列
  - `PATH`: `jenkins-cli.jar` をコマンド実行場所※に配置すること
    - `/work` で実行することを想定し、コンテナ設定で `/work` に配置している
- 各種設定を記載した json ファイル
  - 引数に指定する
  - ```
    {
        // このフォルダ以下のジョブが更新対象(-dc / -u で使用)
        "job_update_urls": [
            "http://localhost:8080/job/job_folder"
        ],
        // これらのジョブ(フォルダも可)がコピー対象(-c / -a で使用)
        // -c の場合はフォルダを指定すること
        // コピー先(dst)がすでに Jenkins 側に存在する場合エラーとなる
        "copy_urls": [
            {
                "src": "http://localhost:8080/job/job_folder1",
                "dst": "http://localhost:8080/job/job_folder2"
            }
        ],
        // job_update_urls の 1 URL 以下や copy_urls の各 dst にあるこれらのジョブを更新する
        "job_names": [
            "job_name_a",
            "job_name_b"
        ],
        // ジョブスクリプトファイルが存在するディレクトリパス
        // ディレクトリがない場合エラー
        "job_script_dir_path"     : "/work/job_script_dir_path",
        // ジョブ更新に使用する xml ファイルを保存するディレクトリパス
        // なければ処理中で生成する
        "update_xml_dir_root_path": "/work/save_xml"
    }
    ```
- オプション:
  - `-dc`, `-c`, `-u`, `-a` はいずれか 1 つを指定すること
  - |略称 |別指定方法                 |説明|
    |---  |---                        |--- |
    |`-dc`|`--download_and_create_xml`|`job_update_urls` 記載の URL 内の `job_names` 記載の各種ジョブの xml をダウンロードし、`job_script_dir_path` 内の当該ジョブのスクリプトファイルを使用して当該ジョブ更新用 xml を生成する|
    |`-u` |`--update`                 |`-dc` の処理実施後、当該ジョブを更新用xml を使用して更新する|
    |`-c` |`--copy`                   |`copy_urls` 記載の `src` ジョブ(フォルダも可)を `dst` にコピーする|
    |`-a` |`--all`                    |`-c` の処理実施後、`dst` 側 URL に対して `-u` の処理実施する|

## out
### `-u`
- json 設定の `update_xml_dir_root_path` ディレクトリ
  - `yyyyMMdd_HHmmss` ディレクトリ
    - json 設定の `job_update_urls` の 1 要素の URL (http文字列) ディレクトリ
      - `ジョブ名.xml` -> スクリプト実行時の当該ジョブの設定内容
      - `ジョブ名_new.xml` -> 更新内容
    - json 設定の `job_update_urls` の 1 要素の URL (http文字列) ディレクトリ
      - ・・・
- json 設定の `job_update_urls` の 1 要素の URL を `ジョブ名_new.xml` で更新した結果(Jenkins 側)

### `-dc`
- json 設定の `update_xml_dir_root_path` ディレクトリ
  - `-u` と同じ

### `-c`
- json 設定の `copy_urls` の 1 要素の `src` を `dst` にコピーした結果(Jenkins 側)

### `-a`
- json 設定の `update_xml_dir_root_path` ディレクトリ
  - `yyyyMMdd_HHmmss` ディレクトリ
    - json 設定の `copy_urls` の 1 要素の `dst` (http文字列) ディレクトリ
      - `ジョブ名.xml` -> スクリプト実行時の当該ジョブの設定内容
      - `ジョブ名_new.xml` -> 更新内容
    - json 設定の `copy_urls` の 1 要素の `dst` (http文字列) ディレクトリ
      - ・・・
- json 設定の `copy_urls` の 1 要素の `src` を `dst` にコピーした上で `ジョブ名_new.xml` で更新した結果(Jenkins 側)

# 4. 実行方法
全てコンテナ内

## 環境変数設定
```
export JENKINS_CLI_USER_NAME=xxxxxxxx
export JENKINS_CLI_USER_NAME=yyyyyyyy

# 以下は docker イメージに組み込んでいるためユーザー操作不要
# /work: jenkins-cli.jar 配置場所
export PATH=${PATH}:/work
```

## 入力例
```
script
 ┗ edit_job.py
job_scripts
 ┗ job_name_a.jenkinsfile
 ┗ job_name_b.java
input.json
 ┗  json 例:
    {
        "job_update_urls": [
            "http://localhost:8080/job/user_work"
        ],
        "copy_urls": [
            {
                "src": "http://localhost:8080/job/user_work",
                "dst": "http://localhost:8080/job/user_work2"
            },
            {
                "src": "http://localhost:8080/job/user_work",
                "dst": "http://localhost:8080/job/user_work3"
            }
        ],
        "job_names": [
            "job_name_a",
            "job_name_b"
        ],
        // ジョブスクリプトファイルが存在するディレクトリパス
        "job_script_dir_path"     : "./job_scripts",
        // ジョブ更新に使用する xml ファイルを保存するディレクトリパス
        "update_xml_dir_root_path": "./save_xml"
    }

http://localhost:8080/
┗ job/user_work
┗ job/user_work2 は存在しない
┗ job/user_work3 はすでに存在する

```

## コマンド
```
cd /work
python3 ./script/edit_job.py -a ./input.json

# ジョブ更新内容を確認するだけの場合
# python3 ./script/edit_job.py -dc ./input.json
```

## 例の -a の結果
```
script                        -> 変化なし
 ┗ edit_job.py
job_scripts                   -> 変化なし
 ┗ job_name_a.jenkinsfile
 ┗ job_name_b.java
input.json                    -> 変化なし
save_xml                      -> ディレクトリが存在しなかったので作成される、以下新規作成
 ┗ yyyyMMdd_HHmmss
    ┗ http___localhost_8080_job_user_work2
      ┗ job_name_a.xml        -> user_work2/job_name_a の内容(＝コピー直後のため、user_work/job_name_a と同一内容)
      ┗ job_name_a_new.xml    -> user_work2/job_name_a に job_scripts/job_name_a.jenkinsfile を設定したもの
      ┗ job_name_b.xml        -> 同 job_name_a
      ┗ job_name_b_new.xml    -> 同 job_name_a_new
    ┗ http___localhost_8080_job_user_work3 はジョブコピーに失敗するのでディレクトリ生成しない

http://localhost:8080/
┗ job/user_work     -> 変化なし
┗ job/user_work2    -> 新規作成
   ┗ job_name_a     -> user_work/job_name_a の内容に http___localhost_8080_job_user_work2/job_name_a_new.xml で更新したジョブ
   ┗ job_name_a     -> user_work/job_name_b の内容に http___localhost_8080_job_user_work2/job_name_b_new.xml で更新したジョブ
┗ job/user_work3    -> 変化なし(コピーに失敗するので何もしない)
```

# 4. スクリプト構成
```
edit_job.py
    ジョブの xml ダウンロード
     -> download_job_xml.py
    ダウンロードした xml に今回更新するジョブスクリプトを上書きして更新用 xml 作成
     -> create_updating_job_xml.py
    更新用 xml を使用してジョブを更新
     -> update_job_by_updating_xml.py
    共通処理
     -> common.py
```

# 5. Licence
- [MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

# 参考: jenkins-cli.jar 使い方
## 動作確認
```
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<password> help
```

## ジョブ設定取得
http://localhost:8080/job/job_auto_update/job/seed_task/ の設定を取得
```
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<password> get-job "job_auto_update/seed_task/"
```

## ジョブ作成
```
# ジョブが存在する場合はエラーする
$ java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<password> create-job "job_auto_update/se
ed_task" < seed_task.xml
```

## ジョブ更新
```
$ java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<password> update-job "job_auto_update/seed_task" < seed_task_new.xml
```

## ジョブ(フォルダ)コピー
```
# dst の URL 末尾が "/" だと NG
$ java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<password> copy-job "job_auto_update/seed_task" "job_auto_update/seed_task2"
```

