# 参考
## Groovy 文法
- まずここから
  - http://simplesandsamples.com/bc.groovy.html
- 次
  - https://qiita.com/opengl-8080/items/b260e4f2df75901239c7
  - https://qiita.com/miyasakura_/items/9d9a8873c333cb9e9f43

## Pipeline
- https://qiita.com/ys1230415/items/51b36fedf1434e877765

# Jenkins pipeline を git 管理スクリプトで動かしたい場合
## GitHub 側
- User -> Setting -> Developer Settings
  - PAT
    - repo にチェックを入れる(これだけでOK)

## Jenkins 側
### Jenkins 全体の Credential 設定
- 不要

### ジョブ設定
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

## 文字コード変えたい場合
- Jenkins サーバーに以下システム環境変数を設定すると、文字コードが UTF-8 になる
  - `JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8`


