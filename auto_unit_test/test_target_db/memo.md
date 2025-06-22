# DB テストする場合
## 前提環境
- jenkins-master コンテナを DinD で立ち上げる
  - 立ち上げ時に `service docker start` しておく

## 手順
- 以降 jenkins-master コンテナ内で作業。DinD で DB コンテナを構築する
```
# DB 環境の前提を作る
# ネットワークがなければ作る(あるかどうかのチェックが必要)
docker network create auto-unit-test-network

# /var/lib/postgresql/data のバインドマウントポイント
# データが残ってると狙い通りの環境にならないので毎回リセットする
rm -rf /mnt/postgres/data
mkdir -p /mnt/postgres/data

# DB コンテナ立ち上げ
# -p 5432:5432 しておく
docker-compose -f testdb.yaml up -d

# localhost:5432 が postgresql インスタンスの入口となる
psql -h localhost -p 5432 -U testdb -d testdb

# これで SQL クエリ定義ファイルをテスト DB に流し込める
psql -f init_tables.sql -h localhost -p 5432 -U testdb -d testdb
```


以上
