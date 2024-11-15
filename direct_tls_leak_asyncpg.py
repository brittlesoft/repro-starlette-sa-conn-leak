import asyncio
import asyncpg

import logging
logging.basicConfig(level=logging.DEBUG)

async def do(i):
    try:
        # connect using direct_tls leads to `unexpected connection_lost() call` when calling conn.close()
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5443/postgres', direct_tls=True)

        # connect using default params works fine
        #conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')

        # lock and simulate work (or block if lock already taken)
        await conn.execute("select pg_advisory_lock(1234)")
        await asyncio.sleep(10)

    except BaseException as e:
        print(i,"got exc:", e, type(e))
        try:
            await conn.close(timeout=2)
        except BaseException as e:
            print(i, "close got exc: ",e)
            # aborting transport here seems to release the connection
            #conn._transport.abort()
            try:
                print(i, "calling terminate")
                conn.terminate()
            except BaseException as e:
                print(i, "terminate got exc: ",e)


async def main():
    ts = []
    for i in range(10):
        ts.append(asyncio.create_task(do(i)))

    async def timeouter():
        await asyncio.sleep(1)
        for t in ts:
            t.cancel()

    asyncio.create_task(timeouter())

    try:
        await asyncio.gather(*ts)
    except asyncio.CancelledError:
        print("cancelled")

    # Sleep so we can observe the state of the connections
    await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())

