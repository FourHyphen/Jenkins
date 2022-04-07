# GitHub 側
- User -> Setting -> Developer Settings
  - PAT
    - repo にチェックを入れる(これだけでOK)

# Jenkins 側
## Jenkins 全体の Credential 設定
- 不要

## ジョブ設定
- Pipeline script from SCM
  - SCM -> Git
    - URL
      - https://github.com/FourHyphen/Jenkins.git
    - 認証
      - 追加
        - ユーザー＆パスワード
          - ユーザー名: 
          - パスワード: GitHub で発行した PAT を入力
    - ブランチ指定子
      - */*
    - Script path
      - LoadOtherScript/Tests/AutoTest.groovy
    - Lightweight checkout
      - チェックは入れてても OK
      - 問題出たら外すのもありらしい

# 参考
## 文字コード変えたい場合
- Jenkins サーバーに以下システム環境変数を設定すると、文字コードが UTF-8 になる
  - `JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8`

