# 環境概要
別ホストのコードを Windows VSCode で編集し、そのファイルを Jenkins 単体テストで参照する環境を作る

## 環境
- Linux ホスト
  - コンテナ
    - Remote Container で接続
    - ここにコードを git clone
    - メモ
      ```
      案(1)
        devcontainer で構築したコンテナを Jenkins ノードとする
         -> devcontainer の Dockerfile に ssh 周りの設定が必要
            22 番ポートをフォワードする際、ポート番号をユーザー毎ユニークにする必要あり
             -> devcontainer.json を編集しないといけない、git 管理そのままとはならない
         -> 当該 `vsc-` コンテナが誰のものかわかりにくい
        Linux ホスト側で git clone が必要
         -> これはユーザー毎にフォルダ分けて git clone してもらえばよい
      
      案(2) -> こっちの方が devcontainer 使わないからわかりやすい
        Linux ホストに Git 管理の Dockerfile 使って docker build してイメージ作る
         -> docker-compose.yaml にポートフォワード設定が必要
            コンテナ内での git clone が必要(docker-compose.yaml にバインドマウント設定してホスト側で git clone もあり)
      ```
- Jenkins サーバー
  - ノード作成
    - Linux ホストのコンテナを登録
  - ジョブ作成
- 上記状態で、
  - 開発時
    - Windows VSCode 起動
    - コンテナに Remote Development で接続してコード編集
  - 単体テスト実行方法
    - Jenkins からジョブ実行
      - ノードは Linux ホスト上のコンテナを指定
      - コンテナで処理が流れる
  - リポジトリへの push
    - VSCode を使用する

## 必要なもの
- Windows VSCode から Remote SSH 機能を使用して Linux ホストのコンテナにアクセス
  - OS への SSH 設定
  - コンテナのベースとなるイメージを作るための Dockerfile
    - Jenkins と接続するための jar を実行できる Java 環境
    - c++ 開発環境
    - python 開発環境
    - javascript 開発環境
    - SQL 環境
  - コンテナを立ち上げる際の docker-compose.yaml
- Jenkins ジョブとしての単体テストの仕組み
- Remote SSH 機能を使用して接続して開発した結果を git push する手段
  - VSCode の GUI を使用

# 環境構築手順
## Windows
- Linux ホストに ssh で接続するための ssh 設定
  - ```
    Windows ユーザーのホームフォルダに秘密鍵を配置(docker build 実行者からもらう)
    場所: c:\Users\＜Windowsユーザー名＞\.ssh
    ```
- VSCode インストール
  - Remote Development 拡張機能インストール

## Linux ホスト
- docker イメージ作成
  - Dockerfile
- docker コンテナ構築
  - docker-compose.yaml

## Jenkins ジョブ作成手順＆実行方法
unit_test と同じ

<br>

以上
