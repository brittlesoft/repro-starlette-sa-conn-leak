import asyncio
import httpx


async def main():

    async def get(url, order):
        async with httpx.AsyncClient() as client:
            res = await client.get(url)  # , timeout=0.5)
            print(res.status_code, res.text, order)

    while True:
        tasks = []
        for i in range(1):
            tasks.append(asyncio.create_task(get("http://localhost:8000/", i)))

        await asyncio.gather(*tasks)
        #await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
