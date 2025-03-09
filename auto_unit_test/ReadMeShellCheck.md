# 環境構築
## 前提
- ReadMe.md に従い、WSL Ubuntu の docker コンテナで jenkins-master 稼働済み

## 概要
- jenkins-master コンテナから ShellCheck をインストールしたコンテナに Jenkins ジョブを投げる

# Jenkins node 構築
## docker コンテナ立ち上げ＆設定
```
docker run -itd \
  --name node-jenkins \
  --net=host \
  -v /mnt:/mnt \
  ubuntu:20.04

docker exec -it node-jenkins bash

mkdir -p /home/jenkins

# java インストール中の time zone 手入力指示を回避
# time zone 手入力するなら apt install 中に以下を指定
#  -  6: Asia
#  - 79: Tokyo
TZ=Asia/Tokyo
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 真に要るのは curl と java と shellcheck くらいだが他用途に使えるようにいろいろ入れておく
apt update && apt install -y \
  curl \
  git \
  git-lfs \
  iputils-ping \
  language-pack-ja \
  less \
  openjdk-17-jre \
  python3-pip \
  shellcheck \
  unzip \
  vim \
  wget \
  zip

python3 -m pip install --upgrade pip && \
ln -s /usr/bin/python3.8 /usr/bin/python

# コンテナ内の日本語表示設定
# vi /etc/locale.gen
#  -> `ja_JP.UTF-8 UTF-8` が有効になるようコメントアウトを外したり行追加
#     面倒なら以下実行
sed -i -e "s/# ja_JP.UTF-8 UTF-8/ja_JP.UTF-8 UTF-8/g" /etc/locale.gen
locale-gen ja_JP.UTF-8
update-locale LANG=ja_JP.UTF-8
echo 'export LANG=ja_JP.UTF-8' >> ~/.bashrc
echo 'export LANGUAGE="ja_JP:ja"' >> ~/.bashrc
source ~/.bashrc
```

## Jenkins ノード作成
- Permanent node にチェックを入れる
- リモートFSルート: `/home/jenkins`
- 起動方法: `Launch agent by connecting it to the controller`
  - 後は初期値
- 可用性: `Keep this agent online as much as possible`
- ノード作成後、ノード画面に表示されるコマンドの `Or run from agent command line, with the secret stored in a file` の方をコンテナ内で実行
  - 例
    ```
    echo 22b6318ffe8447981ea62f2274351c7dbcd8c571a98af64cb1879175242bff02 > secret-file
    curl -sO http://localhost:8080/jnlpJars/agent.jar

    # 最後に & を付けて非同期実行する
    java -jar agent.jar -jnlpUrl http://localhost:8080/computer/shellcheck%2Dnode/jenkins-agent.jnlp -secret @secret-file -workDir "/home/jenkins"
    ```

## Jenkins ノード再立ち上げ
```
docker start node-jenkins
docker exec -it node-jenkins bash
java -jar agent.jar -jnlpUrl http://localhost:8080/computer/shellcheck%2Dnode/jenkins-agent.jnlp -secret @secret-file -workDir "/home/jenkins"
```

# 使い方
- `shellcheck sample.sh`


以上
