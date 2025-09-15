# SJIS Jenkins で SJIS 非対応ノードに SJIS ファイルを文字化けなく load させる方法、結論
- Jenkins ノードの高度な設定から JVM オプションに `-Dfile.encoding=SJIS -Dsun.jnu.encoding=SJIS` を入れれば OK
- ただこれにより UTF-8 ファイルの load に失敗するようになるので、両立は不可っぽい

# SJIS 環境 Jenkins 立ち上げ
## jenkins-master
docker network create sjis-net

docker run -itd \
  --name=jenkins-master-sjis \
  --hostname=jenkins-master-sjis \
  --net=sjis-net \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins-data-sjis:/var/jenkins_home \
  -v /mnt:/mnt \
  -e JAVA_TOOL_OPTIONS="-Dfile.encoding=SJIS -Dsun.jnu.encoding=SJIS" \
  jenkins/jenkins:2.526

## ssh 設定
確か `/var/jenkins_home/.ssh/known_hosts` を空ファイルで良いので作ったような……

# centos7 Jenkins ノード立ち上げ
## ssh 鍵作成
ssh-keygen -t RSA -b 4096

## centos7
docker run コマンドは centos7_jenkins_node_dockerfile 参照

# centos7 sjis 対応記録
## 結論
ここの設定と Jenkins 側の設定は無関係かも？

## メモ
locale -a で一覧見れるっぽい

/etc/sysconfig/i18n

```
$ localedef -f SHIFT_JIS -i ja_JP /usr/lib/locale/ja_JP.sjis
$ locale -a
ja_JP.sjis が追加された

これで sjis ファイル cat の時点で文字化けした(ので load 試してない)

# 使用可能な言語一覧に出てこない
$ localedef --list-archive
en_US.utf8

この状態での locale 一覧
$ locale -a
C
POSIX
en_US.utf8
ja_JP.sjis
```

```
/etc/sysconfig/i18n
  LANG="ja_JP.SJIS"
  SUPPORTED="ja_JP.SJIS:ja_JP:ja"

これで sjis ファイル cat の時点で文字化けした(ので load 試してない)
ファイル削除した
```

```
# ロケールを作成
$ localedef -f SHIFT_JIS -i ja_JP /usr/share/locale/ja_JP.sjis
character map `SHIFT_JIS' is not ASCII compatible, locale not ISO C compliant
 -> 意味: locale が ISO C に準拠していません
 -> /usr/share/locale/ja_JP.sjis が作成されてるので問題ないらしい

localedef --list-archive も locale -a でも状況変わらず

これで sjis ファイル cat の時点で文字化けした(ので load 試してない)

# 明示的に LANG 指定しても状況変わらない
$ export LANG=ja_JP.sjis
$ locale
LANG=ja_JP.SJIS
LC_CTYPE="ja_JP.SJIS"
LC_NUMERIC="ja_JP.SJIS"
LC_TIME="ja_JP.SJIS"
LC_COLLATE="ja_JP.SJIS"
LC_MONETARY="ja_JP.SJIS"
LC_MESSAGES="ja_JP.SJIS"
LC_PAPER="ja_JP.SJIS"
LC_NAME="ja_JP.SJIS"
LC_ADDRESS="ja_JP.SJIS"
LC_TELEPHONE="ja_JP.SJIS"
LC_MEASUREMENT="ja_JP.SJIS"
LC_IDENTIFICATION="ja_JP.SJIS"
LC_ALL=

$ export LC_ALL=ja_JP.SJIS
でも結果は変わらなかった
```

```
サーバーと同じく LANG=C.UTF-8 にしてみるか？
export LANG=C.UTF-8

環境変数は変わったが結果は変わらず
```

```
locale インストールはすでにされてる
$ yum install -y glibc-common
Package glibc-common-2.17-326.el7_9.3.x86_64 already installed and latest version
```

```
https://qiita.com/teruo-oshida/items/08cb84efc2b581b0a439
centos:centos7 はロケールが勝手に制限される
$ cat /etc/yum.conf
...
override_install_langs=en_US.utf8  ★これ
...

なのでこれを消す(これだと ja_JP.utf8 設定だけど)
$ sed -i -e '/override_install_langs/s/$/,ja_JP.utf8/g' /etc/yum.conf

$ yum install -y glibc-common
Package glibc-common-2.17-326.el7_9.3.x86_64 already installed and latest version
最新なので強制インストールが必要らしいが、rpm --force は違うらしい

何か違う？
```

```
# localedef -f SHIFT_JIS -i ja_JP /usr/share/locale/ja_JP.sjis だと /usr/share/locale ではないか？
# デフォルトで参照する場所に作ってみる
$ localedef -f SHIFT_JIS -i ja_JP ja_JP.SJIS

# これで localedef で表示されるようになった
$ localedef --list-archive
en_US.utf8
ja_JP.sjis

# 日本語として UTF-8 も作っておかないといけないか？
#  -> 関係なさそう
$ localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
```

```
AI の回答

# 日本語ロケールを扱うためのパッケージ
yum install -y locales-japanese
 -> No package locales-japanese available.

    # yum-config-manager でEPELリポジトリを有効化（もし未導入の場合）
    yum-config-manager --enable epel

    Shift-JISに関連するパッケージがEPELリポジトリに存在する場合があります。もしlocales-japaneseが直接利用できない場合は、EPELリポジトリを有効化し、必要なパッケージをインストールします。
    yum install -y epel-release
     -> Installed:
          epel-release.noarch 0:7-11
    yum install -y locales-japanese
     -> No package locales-japanese available.
    ★locales-japanese って存在しなさそうなんだが？？？？？？？

# ロケール設定
echo "LANG=ja_JP.SHIFT_JIS" > /etc/locale.conf
echo "LC_ALL=ja_JP.SHIFT_JIS" >> /etc/locale.conf
source /etc/locale.conf
locale
 -> 結果は変わらなかった

# 名前を合わせる
localedef -f SHIFT_JIS -i ja_JP ja_JP.SHIFT_JIS
 -> 結果は変わらなかった 
```

