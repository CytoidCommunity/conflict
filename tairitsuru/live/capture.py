import aiofiles
import httpx


async def capture_stream(url, filename, referer):
    async with httpx.AsyncClient(
            headers={
                "User-Agent":
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) " \
                    "AppleWebKit/537.36 (KHTML, like Gecko) " \
                    "Chrome/76.0.3809.132 " \
                    "Safari/537.36",
                "Referer": referer
            }
    ) as client:
        async with client.stream("GET", url) as stream:
            stream.raise_for_status()
            async with aiofiles.open(filename, "wb") as f:
                async for chuck in stream.aiter_bytes():
                    if chuck:
                        await f.write(chuck)
