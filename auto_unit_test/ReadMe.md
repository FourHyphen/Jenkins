# 環境構築
## WSL(必須)
- powershell で実施
  ```
  wsl --install -d Ubuntu
  ```

## WSL Ubuntu(必須)
- [参考](https://docs.docker.jp/linux/step_one.html)
  - 他にも [こういうところがある](https://zenn.dev/taiga533/articles/11f1b21ef4a5ff)
- WSL Ubuntu 起動方法
  - 多分一番早い: `Windows キー -> ubuntu と入力して ubuntu on windows を選択する`
  - Ubuntu のユーザーパスワードは適当に
- 以下 WSL Ubuntu にて実施
  ```
  # 初期設定
  sudo apt-get update
  sudo apt-get -y upgrade
  # sudo apt-get -y install curl
  
  # docker インストール
  ## OK を確認
  curl -fsSL https://get.docker.com/gpg | sudo apt-key add -
  
  ## 上記 OK 出なくてもとりあえずやってみてください
  ## Docker Desktop を推奨されますが、無視してください
  curl -fsSL https://get.docker.com/ | sh
  
  ## インストール確認
  sudo service docker start
  docker run --rm hello-world
  ```

## WSL Ubuntu(任意)
### docker コマンドに sudo を不要にする設定
- これやらないなら docker コマンドには全部 sudo 付けてください
- [参考](https://qiita.com/DQNEO/items/da5df074c48b012152ee)
  ```
  # docker グループ作って(多分すでにあるけど)そこに今のユーザーを追加する
  sudo groupadd docker
  sudo gpasswd -a $USER docker
  # WSL 閉じて再度表示させれば、docker ps -a 等が sudo 不要になるはずです
  ```

### 没: WSL 使用時に自動で docker daemon を起動する設定
- WSL 使用する度に `sudo service docker start` が必要なのが面倒だったので設定したかった
- 下記設定しても WSL 使用時に .bashrc や .profile が読まれないことがあったため諦めました

<details><summary>没手順(折り畳み)</summary><div>

- [参考](https://zenn.dev/taiga533/articles/11f1b21ef4a5ff)
  ```
  # daemon 起動コマンドの sudo でのパスワード入力回避設定
  sudo visudo
  # エディタにて以下追記して保存(ユーザー名は Ubuntu のもの)
  # GNU エディタの場合、Ctrl + x -> y で保存して終了
  ユーザー名 ALL=NOPASSWD: /usr/sbin/service docker start, /usr/sbin/service docker stop, /usr/sbin/service docker restart
  
  # WSL 使用時の docker daemon 起動設定
  sudo vim $HOME/.bashrc
  # 以下追記して保存
  service docker status > /dev/null 2>&1
  if [ $? = 1 ]; then
    sudo service docker start
  fi
  
  # Ubuntu on WSL でターミナルログイン時に .bashrc を読み込ませる設定
  sudo vim $HOME/.bash_profile
  # 以下記載して保存
  if [[ -f ~/.bashrc ]] ; then
    . ~/.bashrc
  fi
  ```

</div></details>

<br>

# Jenkins 環境構築
## docker イメージ作成
- Jenkins バージョン
  - 絶対にこのバージョンでないといけないという指定はない
  - Pipeline plugin のインストールに成功するバージョンにすること
    - 現状 Pipeline plugin は 2.350 でインストール成功を確認済み
    - インストール失敗したら要バージョンアップ(Dockerfile 編集)
  - [タグ参考](https://hub.docker.com/r/jenkins/jenkins)
- コマンド
  ```
  # WSL 上の ubuntu で実施
  cd docker
  
  # 失敗する場合は --build-arg オプションでプロキシ設定したりなど
  docker build -t jenkins-master-toolgr:2.350 .
  ```

## docker volume 作成
- コマンド
  ```
  # WSL 上の ubuntu で実施
  docker volume create jenkins-data
  ```
- Jenkins 環境構築し直す場合
  - jenkins-data volume に設定を保存しているため、念のためこのボリュームを作り直した方がよいかも

## jenkins-master コンテナ立ち上げ
- コマンド
  ```
  # WSL 上の ubuntu で実施
  docker volume create jenkins-data
  ```

## jenkins 本体設定
- WSL 上の ubuntu で実施
  ```
  # 出てきた文字列を確保
  docker exec jenkins-master bash -c 'cat $JENKINS_HOME/secrets/initialAdminPassword'
  ```
- windows 上のブラウザで実施
  - http://localhost:8080 にアクセス
  - 上記確保した文字列を入れる
  - 左側、install suggested plugin 的な方を選択(selectではない)
  - admin設定(自分専用なので適当でOK)
    - メアドに困ったら @example.com にすれば存在しないことが保証されてる
  - jenkinsurl は http://localhost:8080

# Jenkins ジョブ設定
## 全体構成
- Jenkins ジョブのトップ場所
  - test_suite : フォルダ
    - test_suite_job : pipeline ジョブ
    - unit_test_***  : pipeline ジョブ
    - unit_test_...  : pipeline ジョブ
    - ...

## 内容
- test_suite_job
  - 同階層にある、ジョブ名に `unit_test` を含むジョブを全て実行する
- unit_test_***
  - 単体テストとして作成した jenkinsfile を実行するジョブ
  - どの jenkinsfile を参照するかはビルドパラメーターで変更可能
    - 必ずビルドパラメーターの初期値に設定してください
  - このジョブ単体でも実行可能

# テスト手順
## テスト実施
```
http://localhost:8080 にアクセス
test_suite_job ジョブ開始

他の unit_test_*** を実行できれば環境は OK です
後はテスト作成して通るまでスクリプト修正してテスト実施してください
```

# WSL を再度立ち上げる場合
コンテナ起動が必要。docker サービスが立ち上がっていないのでそこから。

```
# docker daemon 起動
sudo service docker start

# Jenkins サーバー起動
docker start jenkins-master
```

<br>

以上
