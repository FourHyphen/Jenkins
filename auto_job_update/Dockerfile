FROM ubuntu:20.04

# java インストール中の time zone 手入力指示を回避
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# (1) apt
#     python は ubuntu:20.04 デフォルトの 3.8 を使用
#     iputils-ping   -> ping コマンド
#     openjdk-17-jre -> java コマンド
# (2) python 周り
#     pip 更新
#     python3.8 を python コマンドで使えるようシンボリックリンク作成
RUN apt -y update && \
    apt -y install \
        curl \
        git \
        git-lfs \
        iputils-ping \
        openjdk-17-jre \
        python3-pip \
        unzip \
        vim \
        zip && \
    python3 -m pip install --upgrade pip && \
    ln -s /usr/bin/python3.8 /usr/bin/python        

# 各種ディレクトリ作成＆作業ディレクトリ設定設定
RUN mkdir -p /work/git && mkdir /host
WORKDIR /work

# jenkins-cli.jar 配置
COPY jenkins-cli.jar /work/jenkins-cli/
ENV PATH $PATH:/work/jenkins-cli

# スクリプト配置
COPY job_update_script/ /work/job_update_script/