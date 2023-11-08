# 1. 概要
- 環境構築
  - イメージビルド
  - コンテナ起動
  - コンテナ内で git clone
- スクリプト実行
  - 各種スクリプトを実行して Jenkins ジョブ更新

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

## git clone
- コンテナ内で作業
- `/work/git` で ` git clone`
  - 認証情報は自身で指定

# 3. スクリプト実行
## 構成
```
update_job_all.py
    for ジョブ URL in 更新したい全てのジョブ URL
        for ジョブ in 更新したい全てのジョブ
            update_job.py
                ベース xml ダウンロード
                 -> download_job_xml.py
                ベース xml に今回更新するジョブスクリプトを上書きして更新用 xml 作成
                 -> create_updating_job_xml.py
                update_job_by_updating_xml.py
                 -> 更新用 xml を使用してジョブを更新
```

## 実行方法
### 設定
`update_job_all.py` の以下を設定
```
# この URL 以下全てのジョブが更新候補
G_JOB_DIR_URLS = ['http://localhost:8080/job/job_auto_update',
                  'http://localhost:8080/job/job_auto_update2']

# 更新するジョブ名
G_JOB_NAMES = ['build', 'seed_task']
```

以下環境変数を設定

```
JENKINS_CLI_USER_NAME: ユーザー名
JENKINS_CLI_PASSWORD : パスワード
```

### 実行
```
update_job_all.py ＜ジョブスクリプトファイルが存在するディレクトリパス＞ ＜ジョブ更新に使用した xml ファイルを保存するディレクトリパス＞
```

例
```
script
 ┗ update_job_all.py
job_scripts
 ┗ build.jenkinsfile
 ┗ seed_task.java
save_job_xml

コマンド
python3 ./script/update_job_all.py ./job_scripts ./save_job_xml
```

例の結果
```
script               -> 変化なし
 ┗ update_job_all.py
job_scripts          -> 変化なし
 ┗ build.jenkinsfile
 ┗ seed_task.java
save_job_xml         -> もしこのディレクトリが存在しなかった場合、作成される
 ┗ build_new.xml     -> 作成される
 ┗ seed_task_new.xml -> 作成される
```

# 4. Licence
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

