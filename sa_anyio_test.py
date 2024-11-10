import asyncio
import asyncpg
import anyio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_size=1, max_overflow=0, echo_pool="debug")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def tg_wrapper(func, *args, **kwargs):
    async with anyio.create_task_group() as tg:
        tg.start_soon(func, *args, **kwargs)

async def querier():
    async with async_session() as session, session.begin():
        res = await session.execute(text("select 1"))
        print([row for row in res])
        await asyncio.sleep(10)

async def main():

    while True:
        t = asyncio.create_task(tg_wrapper(querier))

        async def timeouter():
            await asyncio.sleep(1)
            t.cancel()

        asyncio.create_task(timeouter())

        try:
            await t
        except asyncio.CancelledError:
            print("cancelled")

if __name__ == '__main__':
    asyncio.run(main())
