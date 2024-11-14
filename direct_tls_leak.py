import asyncio
import asyncpg
import anyio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

# direct_tls seems to be the key to seeing the issue
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5443/postgres?direct_tls=true"

# pool_size must be >1
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_size=2, max_overflow=0, echo_pool="debug")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def querier():
    async with async_session() as session, session.begin():
        # locking rows is important for reproducing the issue
        res = await session.execute(text("select * from test for update;"))
        print([row for row in res])

        # simulate more asyncio work while tx is open and lock is held
        # task will be cancelled during this
        await asyncio.sleep(10)

async def main():

    async with async_session() as session, session.begin():
        res = await session.execute(text("create table if not exists test (a text);"))
        print(res)
        res = await session.execute(text("insert into test values ('patate');"))
        print(res)

    while True:
        ts = []
        for i in range(3):  # 1 more than pool size
            ts.append(asyncio.create_task(querier()))

        async def timeouter():
            await asyncio.sleep(1)
            for t in ts:
                t.cancel()

        asyncio.create_task(timeouter())

        try:
            await asyncio.gather(*ts)
        except asyncio.CancelledError:
            print("cancelled")

if __name__ == '__main__':
    asyncio.run(main())

