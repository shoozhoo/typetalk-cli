typetalk-cli
============

Typetalk cli is Typetalk(https://typetalk.in) cli client.

Install
=======
Need Python 2.7
    sudo pip install git+https://github.com/shoozhoo/typetalk-cli.git

Usage
=====
Add account(Cient credential)
-----------------------------
```
ttc account -a
```
You can add multiple accounts.

Show accounts
-------------
```
ttc account
```
Output example
```
Current account: foo
Stored accounts:
                 foo
                 bar
```

Switch account
--------------
```
ttc account bar
```

Show topic list
---------------
```
ttc list [-f] [-u]
```
positional arguments:
* TOPIC_ID    your topic_id

optional arguments:
* -f  show favorite only
* -u  show unread only

Show message in topic
---------------------
```
ttc topic [-h] [-n COUNT] [-f] [-b] TOPIC_ID
```
positional arguments:
* TOPIC_ID    your topic_id

optional arguments:
* -n COUNT    message counts
* -f          follow like "tail -f"
* -b          set read flag

Post message
------------
```
ttc post [-h] [-t TALK] [-a FILE] TOPIC_ID [MESSAGE]
```
positional arguments:
* TOPIC_ID    your topic_id
* MESSAGE     if you do not specify, use stdin

optional arguments:
* -h, --help  show this help message and exit
* -t TALK     talk_id
* -a FILE     attachment file
