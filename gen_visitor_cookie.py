import aiohttp
import asyncio
import json
import re
import uuid


async def get_weibo_sub():
    url = "https://passport.weibo.com/visitor/genvisitor2"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    data = {
        'cb': 'visitor_gray_callback',
        'ver': '20250916',
        'request_id': uuid.uuid4().hex,
        'tid': '',
        'from': 'weibo',
        'webdriver': 'false',
    }

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
