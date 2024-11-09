# repro-starlette-sa-conn-leak

Reproduction code for a sql connection leak that happens when the task handling the http request is cancelled with `task.cancel()`, but only if a `BaseHTTPMiddleware` is present in the middleware stack.

Requirements:
- docker
- poetry
- python (tested on 3.12)


first, install deps:
```
poetry install
```

Then, possibly in a terminal multiplexer, run the following:

```
# postgres
docker compose up db

# postgres conn watcher
bash watch_pg.sh

# server
make run

# client
poetry run python client.py
```

The number of connections shown in the watch_pg pane should never go above 6 (pool size + 1 for watcher).

When running with the `PassMiddleware` enabled, the number of connection goes up.
When it isn't present in the middleware stack, the connections are closed as expected.
