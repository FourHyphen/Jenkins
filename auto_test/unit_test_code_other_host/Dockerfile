# # docker build --network host -t "my-development" ./
# # ssh 設定を変更して build し直す場合は --no-cache オプションを付与すること
## docker build コマンド実行者がやること
#   -> ./ssh に以下 4 種の公開鍵＆秘密鍵があることを確認
#     ない場合:
#       i) docker build を実行する Linux ホストで以下実行
#         cd <この Dockerfile のあるディレクトリ>
#         ssh-keygen -t rsa -N "" -f ./ssh/ssh_host_rsa_key
#         ssh-keygen -t dsa -N "" -f ./ssh/ssh_host_dsa_key
#         ssh-keygen -t ecdsa -N "" -f ./ssh/ssh_host_ecdsa_key
#         ssh-keygen -t ed25519 -N "" -f ./ssh/ssh_host_ed25519_unit_test_development_key
#       ii) 上記公開鍵＆秘密鍵を本 Dockerfile のディレクトリ/ssh/ に配置(上記コマンドを実行していればそうなる)
#       iii) ssh_host_ed25519_unit_test_development_key (秘密鍵の方) をユーザーに展開し、c:\Users\<ユーザー名>\.ssh\ に配置してもらう
FROM ubuntu:24.04

# インストール中の time zone 手入力指示を回避
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 一通りインストール
#     iputils-ping   -> ping コマンド
# Java
#     バージョンは暫定のため注意
RUN apt update -y \
    && apt install -y \
        curl \
        git \
        git-lfs \
        iputils-ping \
        openjdk-17-jre \
        shellcheck \
        unzip \
        vim \
        wget \
        zip

# python
#     ubuntu:24.04 デフォルトでは python2 も 3 もないので 3 をインストール
#     pip 更新＆パッケージインストール
#     python3 を python コマンドで使えるようシンボリックリンク作成
RUN apt update -y \
    && apt install -y \
        python3 \
        python3-pip \
        # python3-venv \
        python3-dev \
    # pip はシステム側を直接更新ではなく仮想環境上で作業するのが推奨だが、docker 自体が仮想環境のためシステム側に直接変更を適用する
    # && python3 -m venv --upgrade-deps myenv \
    # && source myenv/bin/activate \
    && apt install --only-upgrade python3-pip \
    && pip install --break-system-packages \
        pyyaml \
        pytest \
    && ln -s /usr/bin/python3 /usr/bin/python

# SQL 環境
RUN apt update -y \
    && apt install -y \
        postgresql

# SQL 検証環境構築手順を検証するために docker インストール
RUN apt update \
    && apt install -y \
        ca-certificates \
        gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt update \
    && apt install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io

# docker compose V1 をインストール
RUN curl \
        -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# javascript
#     TODO: 単体テスト環境

# c++ 開発環境
RUN apt update -y \
    && apt install -y \
        gcc \
        g++ \
        make

# cmake インストール(途中タイムライン入力が求められて複雑なので別ファイルで実行)
COPY ./install_cmake.sh /install_cmake.sh
RUN apt update \
    && apt install -y expect \
    && chmod +x /install_cmake.sh \
    && bash /install_cmake.sh

# # c++ 自動テストに Google test を使用、準備
# # 参考: https://qiita.com/shohirose/items/30e39949d8bf990b0462
# RUN apt update \
#     && apt install -y ninja-build \
#     && apt install -y expect
# 
# # Google test インストール(wget を前もってインストールしておくこと)
# RUN wget https://github.com/google/googletest/archive/refs/tags/release-1.11.0.tar.gz \
#     && tar zxvf release-1.11.0.tar.gz \
#     && cd googletest-release-1.11.0 \
#     && cmake -G Ninja -S . -B build \
#     && cmake --build build \
#     && cmake --install build \
#     && cd ../ \
#     && rm release-1.11.0.tar.gz \
#     && rm -rf googletest-release-1.11.0

# 念のため root パスワード設定
RUN echo 'root:root' | chpasswd

# sshd 設定
RUN mkdir -p /etc/ssh \
    && mkdir -p /var/run/sshd \
    && mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh

RUN apt update -y \
    && apt install -y openssh-server \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
    # && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config \
    # && chmod 600 ~/.ssh/authorized_keys

COPY ./ssh/ssh_host_rsa_key                               /etc/ssh/ssh_host_rsa_key
COPY ./ssh/ssh_host_dsa_key                               /etc/ssh/ssh_host_dsa_key
COPY ./ssh/ssh_host_ecdsa_key                             /etc/ssh/ssh_host_ecdsa_key
COPY ./ssh/ssh_host_ed25519_unit_test_development_key     /etc/ssh/ssh_host_ed25519_key
COPY ./ssh/ssh_host_ed25519_unit_test_development_key.pub /root/.ssh/authorized_keys

# ssh 鍵のパーミッション設定
RUN chmod 600 /etc/ssh/ssh_host_rsa_key \
    && chmod 600 /etc/ssh/ssh_host_dsa_key \
    && chmod 600 /etc/ssh/ssh_host_ecdsa_key \
    && chmod 600 /etc/ssh/ssh_host_ed25519_key \
    && chmod 600 /root/.ssh/authorized_keys

# ssh ポート公開
EXPOSE 22

# 使用済みの apt キャッシュを削除
RUN rm -rf /var/lib/apt/lists/*

# # ENTRYPOINT での sshd 起動はコンテナ再起動時に上手くいかなかったため compose 側で指定する
# ENTRYPOINT ["/usr/sbin/sshd", "-D", "-d"]
