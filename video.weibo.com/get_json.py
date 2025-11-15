import aiohttp
import asyncio
import json

async def fetch_video_info():
    url = "https://weibo.com/tv/api/component?page=%2Ftv%2Fshow%2F1034%3A5233218052358208"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://weibo.com/tv/show/1034:5233218052358208?from=old_pc_videoshow',
        'cookie': 'SUB=_2AkMeRI2Gf8NxqwFRmv0XxG7naIRxww7EieKoGHxdJRMxHRl-yT8XqmAjtRB6NcSjaQuDxONKyketwlSy144ie5Fy4foI'
    }
    
    # POST 数据（form-urlencoded 格式）
    payload = {
        'data': '{"Component_Play_Playinfo":{"oid":"1034:5233218052358208"}}'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            print(f"响应状态码: {response.status}")
            
            if response.status == 200:
                result = await response.json()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                text = await response.text()
                print(f"响应内容: {text}")

asyncio.run(fetch_video_info())
