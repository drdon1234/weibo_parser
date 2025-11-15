import aiohttp
import asyncio
import json
import re


async def get_weibo_sub():
    url = "https://visitor.passport.weibo.cn/visitor/genvisitor2"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'content-type': 'application/x-www-form-urlencoded',
    }

    # 仅需要一个参数
    data = {'cb': 'visitor_gray_callback'}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            text = await response.text()
            match = re.search(r'visitor_gray_callback\((.*)\)', text)

            if match:
                result = json.loads(match.group(1))
                sub = result.get('data', {}).get('sub', '')
                print(sub)
            else:
                print("解析失败")


asyncio.run(get_weibo_sub())
