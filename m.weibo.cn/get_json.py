import aiohttp
import asyncio

async def fetch_weibo_detail():
    url = "https://m.weibo.cn/detail/5221716881314113"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://visitor.passport.weibo.cn/',
        'cookie': 'SUB=_2AkMeRINtf8NxqwFRmv0XxG7naIRxww7EieKoGHK2JRM3HRl-yT8XqkcAtRB6NcStgqfDHDV-HvvlUUNqCwijrueu6DaN',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"状态码: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            text = await response.text()
            print(f"\n响应长度: {len(text)} 字符")
            print(f"\n{text}")

asyncio.run(fetch_weibo_detail())
