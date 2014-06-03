typetalk-cli
============

Typetalk cli はTypetalk(https://typetalk.in)のコマンドライン用クライアントです。

インストール
=======
要Python 2.7
```
sudo pip install git+https://github.com/shoozhoo/typetalk-cli.git
```

使い方
=====
アカウントの追加(Cient credential)
--------------------------------
```
ttc account -a
```
まずアカウントを登録必要があります。
Developerページ(https://typetalk.in/my/develop/applications )からアプリケーションを登録してください。
Grant Type は Client Credentials を選択して、生成されるClient ID, Client Secretを ttc に入力します。
複数のアカウントを登録する事ができます。

登録済みアカウントを表示
---------------------
```
ttc account
```
出力例
```
Current account: foo
Stored accounts:
                 foo
                 bar
```
Current account が現在利用されているアカウントです。
Stored accounts が登録済みのアカウントの一覧になります。

アカウントの切り替え
-----------------
```
ttc account bar
```
登録済みの別のアカウントを利用するようにアカウントを切り替えます。

トピックの一覧を表示
---------------
```
ttc list [-f] [-u]
```

オプション:
* -f  お気に入りのトピックだけを表示します。
* -u  未読のあるトピックだけを表示します。

トピックのメッセージを表示
---------------------
```
ttc topic [-h] [-n COUNT] [-f] [-b] TOPIC_ID
```
引数:
* TOPIC_ID    表示するトピックのID

オプション:
* -n COUNT    表示するメッセージ数
* -f          "tail -f"の様に新しいメッセージを監視する
* -b          表示したメッセージを既読にする

メッセージを投稿
--------------
```
ttc post [-h] [-t TALK] [-a FILE] TOPIC_ID [MESSAGE]
```
引数:
* TOPIC_ID    投稿するトピックのID
* MESSAGE     投稿するメッセージ。省略時は標準入力から入力します。

オプション:
* -t TALK     トーク(まとめ)に含める場合にトークIDを指定します。
* -a FILE     添付するファイルを指定します。

-t, -aオプションは複数回指定することができます。
