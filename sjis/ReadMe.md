# SJIS Jenkins �� SJIS ��Ή��m�[�h�� SJIS �t�@�C���𕶎������Ȃ� load ��������@�A���_
- Jenkins �m�[�h�̍��x�Ȑݒ肩�� JVM �I�v�V������ `-Dfile.encoding=SJIS -Dsun.jnu.encoding=SJIS` ������� OK
- ��������ɂ�� UTF-8 �t�@�C���� load �Ɏ��s����悤�ɂȂ�̂ŁA�����͕s���ۂ�

# SJIS �� Jenkins �����グ
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

## ssh �ݒ�
�m�� `/var/jenkins_home/.ssh/known_hosts` ����t�@�C���ŗǂ��̂ō�����悤�ȁc�c

# centos7 Jenkins �m�[�h�����グ
## ssh ���쐬
ssh-keygen -t RSA -b 4096

## centos7
docker run �R�}���h�� centos7_jenkins_node_dockerfile �Q��

# centos7 sjis �Ή��L�^
## ���_
�����̐ݒ�� Jenkins ���̐ݒ�͖��֌W�����H

## ����
locale -a �ňꗗ�������ۂ�

/etc/sysconfig/i18n

```
$ localedef -f SHIFT_JIS -i ja_JP /usr/lib/locale/ja_JP.sjis
$ locale -a
ja_JP.sjis ���ǉ����ꂽ

����� sjis �t�@�C�� cat �̎��_�ŕ�����������(�̂� load �����ĂȂ�)

# �g�p�\�Ȍ���ꗗ�ɏo�Ă��Ȃ�
$ localedef --list-archive
en_US.utf8

���̏�Ԃł� locale �ꗗ
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

����� sjis �t�@�C�� cat �̎��_�ŕ�����������(�̂� load �����ĂȂ�)
�t�@�C���폜����
```

```
# ���P�[�����쐬
$ localedef -f SHIFT_JIS -i ja_JP /usr/share/locale/ja_JP.sjis
character map `SHIFT_JIS' is not ASCII compatible, locale not ISO C compliant
 -> �Ӗ�: locale �� ISO C �ɏ������Ă��܂���
 -> /usr/share/locale/ja_JP.sjis ���쐬����Ă�̂Ŗ��Ȃ��炵��

localedef --list-archive �� locale -a �ł��󋵕ς�炸

����� sjis �t�@�C�� cat �̎��_�ŕ�����������(�̂� load �����ĂȂ�)

# �����I�� LANG �w�肵�Ă��󋵕ς��Ȃ�
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
�ł����ʂ͕ς��Ȃ�����
```

```
�T�[�o�[�Ɠ����� LANG=C.UTF-8 �ɂ��Ă݂邩�H
export LANG=C.UTF-8

���ϐ��͕ς���������ʂ͕ς�炸
```

```
locale �C���X�g�[���͂��łɂ���Ă�
$ yum install -y glibc-common
Package glibc-common-2.17-326.el7_9.3.x86_64 already installed and latest version
```

```
https://qiita.com/teruo-oshida/items/08cb84efc2b581b0a439
centos:centos7 �̓��P�[��������ɐ��������
$ cat /etc/yum.conf
...
override_install_langs=en_US.utf8  ������
...

�Ȃ̂ł��������(���ꂾ�� ja_JP.utf8 �ݒ肾����)
$ sed -i -e '/override_install_langs/s/$/,ja_JP.utf8/g' /etc/yum.conf

$ yum install -y glibc-common
Package glibc-common-2.17-326.el7_9.3.x86_64 already installed and latest version
�ŐV�Ȃ̂ŋ����C���X�g�[�����K�v�炵�����Arpm --force �͈Ⴄ�炵��

�����Ⴄ�H
```

```
# localedef -f SHIFT_JIS -i ja_JP /usr/share/locale/ja_JP.sjis ���� /usr/share/locale �ł͂Ȃ����H
# �f�t�H���g�ŎQ�Ƃ���ꏊ�ɍ���Ă݂�
$ localedef -f SHIFT_JIS -i ja_JP ja_JP.SJIS

# ����� localedef �ŕ\�������悤�ɂȂ���
$ localedef --list-archive
en_US.utf8
ja_JP.sjis

# ���{��Ƃ��� UTF-8 ������Ă����Ȃ��Ƃ����Ȃ����H
#  -> �֌W�Ȃ�����
$ localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
```

```
AI �̉�

# ���{�ꃍ�P�[�����������߂̃p�b�P�[�W
yum install -y locales-japanese
 -> No package locales-japanese available.

    # yum-config-manager ��EPEL���|�W�g����L�����i�����������̏ꍇ�j
    yum-config-manager --enable epel

    Shift-JIS�Ɋ֘A����p�b�P�[�W��EPEL���|�W�g���ɑ��݂���ꍇ������܂��B����locales-japanese�����ڗ��p�ł��Ȃ��ꍇ�́AEPEL���|�W�g����L�������A�K�v�ȃp�b�P�[�W���C���X�g�[�����܂��B
    yum install -y epel-release
     -> Installed:
          epel-release.noarch 0:7-11
    yum install -y locales-japanese
     -> No package locales-japanese available.
    ��locales-japanese ���đ��݂��Ȃ������Ȃ񂾂��H�H�H�H�H�H�H

# ���P�[���ݒ�
echo "LANG=ja_JP.SHIFT_JIS" > /etc/locale.conf
echo "LC_ALL=ja_JP.SHIFT_JIS" >> /etc/locale.conf
source /etc/locale.conf
locale
 -> ���ʂ͕ς��Ȃ�����

# ���O�����킹��
localedef -f SHIFT_JIS -i ja_JP ja_JP.SHIFT_JIS
 -> ���ʂ͕ς��Ȃ����� 
```

