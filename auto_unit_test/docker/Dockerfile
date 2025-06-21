FROM jenkins/jenkins:2.350

# docker build -t jenkins-master-toolgr:2.350 .
# jenkins/jenkins には sudo がないので root で実行する
USER root

RUN apt-get update && \
    apt-get install -y \
      build-essential \
      git \
      jq \
      postgresql \
      python3-pip \
      python3-venv \
      python3-dev \
      shellcheck \
      unzip \
      wget

# Debian への docker cli インストール準備: apt リポジトリの追加
RUN apt-get update && \
    apt-get install -y \
      ca-certificates \
      curl \
      gnupg \
      lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | \
      gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

# Debian への docker cli インストール
RUN apt-get update && \
    apt-get install -y \
      docker-ce \
      docker-ce-cli \
      containerd.io

# docker compose V1 をインストール
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

RUN pip3 install --upgrade pip && \
    pip3 install \
      pytest \
      pyyaml

ENTRYPOINT ["bash", "-c", "service docker start && /usr/bin/tini -- /usr/local/bin/jenkins.sh"]
