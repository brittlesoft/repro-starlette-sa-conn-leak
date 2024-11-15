# SA / asyncpg sql connection leaks reproducers

Reproduction code for 2 sql connection leaks that happen when cancelling tasks holding sql sessions.

1. When an anyio taskgroup is cancelled while a task in the group holds an open transaction, the
   underlying connection is leaked.
   Reproduce with `sa_anyio_test.py`.
   (see https://github.com/sqlalchemy/sqlalchemy/pull/12076 for discussion)
2. When using asyncpg + `direct_tls=true` to connect to postgres, cancelling a task (asyncio) that
   holds a transaction + a row lock, the underlying connection can leak.
   Reproduce with `direct_tls_leak.py` or `direct_tls_leak_asyncpg.py`.

   I used nginx to terminate the tls connection, this is similar to what "google cloudsql connector"
   does, which is where we first observed the issue "in the wild".


Requirements:
- docker
- poetry
- python (tested on 3.12)


first, install deps:
```
# possibly install python 3.12 with pyenv
poetry install
```

Then, possibly in a terminal multiplexer, run the following:

```
# postgres
docker compose up

# postgres conn watcher
bash watch_pg.sh

# first leak
poetry run python sa_anyio_test.py

# second leak
poetry run python direct_tls_leak.py
```

The number of connections shown in the watch_pg pane will steadily increase, but it should never go
above pool size + watcher connection.

# direct_tls_leak_asyncpg.py

A refined reproducer of the second leak can be found in `direct_tls_leak_asyncpg.py`, where asyncpg
tasks are cancelled while waiting for pg. This leads to `conn.close()` throwing `unexpected
connection_lost() call` and leaving the connection open.
After this exception, calling `conn.terminate()` does not close the connection either.

