from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql import text
import asyncio

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@172.18.0.2/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_size=1, max_overflow=0, echo_pool="debug")
async_session = async_sessionmaker(engine, expire_on_commit=False)


class PassMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        return await call_next(request)


class TimeoutMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        send_called = False

        async def register_send(msg):
            nonlocal send_called
            send_called = True
            await send(msg)

        task = asyncio.create_task(self.app(scope, receive, register_send))

        async def wait_and_cancel():
            await asyncio.sleep(0.5)
            if send_called is not True:
                r = JSONResponse({"error": "cancelled"})
                await r(scope, receive, send)
            task.cancel()
            print("cancelled")

        asyncio.create_task(wait_and_cancel())
        try:
            await task
        except asyncio.CancelledError:
            pass


async def homepage(request):
    async with async_session() as session, session.begin():
        #res = await session.execute(text("select pg_sleep(0.2)"))

        c = await session.connection()
        raw = await c.get_raw_connection()
        print("in http handler:",raw.driver_connection._transport._sock)
        res = await session.execute(text("select 1"))
        await asyncio.sleep(0.6)
        return JSONResponse({"hello": [str(row) for row in res]})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
    ],
    middleware=[
        Middleware(TimeoutMiddleware),
        Middleware(PassMiddleware),
    ],
)
