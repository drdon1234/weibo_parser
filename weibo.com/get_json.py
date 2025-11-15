import aiohttp
import asyncio
import json


async def fetch_weibo_data():
    # 目标 URL
    url = "https://weibo.com/ajax/statuses/show?id=5232446897127970"

    # 设置请求头
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://weibo.com/1566936885/5232446897127970',
        'cookie': 'SUB=_2AkMeSxBBf8NxqwFRmv0Wzmvlb4lyywvEieKoF-GaJRMxHRl-yT9xqmkNtRB6Ncs-rn0HdnUCxqIikqZO780YWSpLBuLV',
    }

    # 创建 aiohttp 会话并发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # 检查响应状态
            print(f"响应状态码: {response.status}")
            print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
            print("\n" + "=" * 60)
            print("JSON 响应内容:")
            print("=" * 60 + "\n")

            if response.status == 200:
                # 获取 JSON 响应
                json_data = await response.json()

                # 格式化打印 JSON（美化输出）
                print(json.dumps(json_data, ensure_ascii=False, indent=2))

                # 或者直接打印原始内容
                # print(json_data)
            else:
                # 如果请求失败，打印响应文本
                text = await response.text()
                print(f"请求失败: {text}")


# 运行异步函数
if __name__ == "__main__":
    asyncio.run(fetch_weibo_data())
