# 1. 概要
- 環境構築
  - イメージビルド
  - コンテナ起動
  - コンテナ内にジョブスクリプトファイルを配置
- スクリプト実行
  - Jenkins ジョブの現在の設定に、ジョブスクリプトファイルの中身を上書きする方法で Jenkins ジョブ更新

# 2. 環境構築
## イメージビルド方法
```
cd <Dockerfile 置いたディレクトリ>
docker build -f ./Dockerfile -t update-jenkins-job:latest .
```

## コンテナ起動方法
```
cd <docker-compose yml 置いたディレクトリ>
docker-compose -f dc_update_jenkins_job.yml up -d
```

## 更新に使用するジョブスクリプトをコンテナに配置
- パスはどこでも OK

# 3. in/out
全てコンテナ内

## in
- 各種設定を記載した json ファイル
  - ```
    {
        // このフォルダ以下のジョブが更新対象
        "job_dir_urls": [
            "http://localhost:8080/job/job_folder"
        ],
        // job_dir_urls の 1 URL 以下にあるこれらのジョブを更新する
        "job_names": [
            "job_name_a",
            "job_name_b"
        ],
        // ジョブスクリプトファイルが存在するディレクトリパス
        // ディレクトリがない場合エラー
        "job_script_dir_path"     : "/work/git/job_script_dir_path",
        // ジョブ更新に使用する xml ファイルを保存するディレクトリパス
        // なければ処理中で生成する
        "update_xml_dir_root_path": "/work/save_xml"
    }
    ```
- 環境変数
  - `JENKINS_CLI_USER_NAME`: Jenkins ユーザー名
  - `JENKINS_CLI_PASSWORD`: Jenkins ユーザーのパスワード or トークン文字列
  - `PATH`: `jenkins-cli.jar` にパスが通っていること
    - PATH はコンテナ設定に含めているため基本編集不要
- `-r` の有無
  - `-r` をつけるとジョブ更新に使用する xml を生成するまでを行い、実際の更新は行わない
    - 更新内容確認用を想定

## out
- `update_xml_dir_root_path` ディレクトリ
  - `yyyyMMdd_HHmmss` ディレクトリ
    - job_dir_urls の 1 要素(http文字列) ディレクトリ
      - `ジョブ名.xml` -> スクリプト実行時の当該ジョブの設定内容
      - `ジョブ名_new.xml` -> 更新内容
    - job_dir_urls の 1 要素(http文字列) ディレクトリ
      - ・・・
- job_dir_urls の 1 要素(Jenkins ジョブ)
  - `ジョブ名_new.xml` で更新
  - `-r` を付けた場合は更新しない

# 4. 実行方法
全てコンテナ内

## 環境変数設定
```
export JENKINS_CLI_USER_NAME=xxxxxxxx
export JENKINS_CLI_USER_NAME=yyyyyyyy
```

## 入力例
```
script
 ┗ update_job_all.py
job_scripts
 ┗ build.jenkinsfile
 ┗ seed_task.java
input.json
 ┗  {
        "job_dir_urls": [
            "http://localhost:8080/job/job_folder1",
            "http://localhost:8080/job/job_folder2"
        ],
        "job_names": [
            "build",
            "seed_task"
        ],
        "job_script_dir_path"     : "./job_scripts",
        "update_xml_dir_root_path": "./save_xml"
    }
```

## コマンド
```
python3 ./script/update_job_all.py ./input.json

# ジョブ更新内容を確認するだけの場合
# python3 ./script/update_job_all.py -r ./input.json
```

## 例の結果
```
script                  -> 変化なし
 ┗ update_job_all.py
job_scripts             -> 変化なし
 ┗ build.jenkinsfile
 ┗ seed_task.java
input.json              -> 変化なし
save_xml                -> ディレクトリが存在しなかったので作成される
 ┗ yyyyMMdd_HHmmss      -> 以下新規作成
    ┗ http___localhost_8080_job_job_folder1
      ┗ build.xml         -> job_folder1/build の内容
      ┗ build_new.xml     -> job_folder1/build に job_scripts/build.jenkinsfile を設定したもの
      ┗ seed_task.xml     -> 同 build
      ┗ seed_task_new.xml -> 同 build_new
    ┗ http___localhost_8080_job_job_folder2
      ┗ build.xml         -> job_folder2/build の内容
      ┗ build_new.xml     -> job_folder2/build に job_scripts/build.jenkinsfile を設定したもの
      ┗ seed_task.xml     -> 同 build
      ┗ seed_task_new.xml -> 同 build_new
```

# 4. スクリプト構成
```
update_job_all.py
    for ジョブ URL in 更新したい全てのジョブ URL
        for ジョブ in 更新したい全てのジョブ
            ベース xml ダウンロード
                -> download_job_xml.py
            ベース xml に今回更新するジョブスクリプトを上書きして更新用 xml 作成
                -> create_updating_job_xml.py

            if not "-r"
                update_job_by_updating_xml.py
                    -> 更新用 xml を使用してジョブを更新
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

