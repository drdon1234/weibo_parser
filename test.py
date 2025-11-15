# -*- coding: utf-8 -*-
"""
微博解析器测试脚本
测试三种类型的微博链接解析
"""
import asyncio
import aiohttp
import json
from weibo_parser import WeiboParser


async def test_single_url(parser: WeiboParser, session: aiohttp.ClientSession, url: str):
    """测试单个URL的解析
    
    Args:
        parser: 微博解析器实例
        session: aiohttp 会话
        url: 要测试的URL
    """
    print("\n" + "=" * 80)
    print(f"测试 URL: {url}")
    print("=" * 80)
    
    # 检查是否可以解析
    if not parser.can_parse(url):
        print(f"❌ 无法解析此 URL: {url}")
        return
    
    try:
        # 解析 URL
        result = await parser.parse(session, url)
        
        # 打印结果
        print("✅ 解析成功！")
        print("-" * 80)
        print(f"原始 URL: {result['url']}")
        print(f"媒体类型: {result['media_type']}")
        print(f"作者: {result['author']}")
        print(f"简介: {result['desc'][:200] if result['desc'] else '(无)'}")
        print(f"上传时间: {result['timestamp']}")
        print(f"媒体文件数量: {len(result['media_urls'])}")
        
        # 显示媒体链接
        if result['media_urls']:
            print("\n媒体链接:")
            for i, media_url in enumerate(result['media_urls'], 1):
                print(f"  {i}. {media_url[:120]}...")
        
        print("\n完整结果 (JSON):")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("=" * 80)
    print("微博解析器测试")
    print("=" * 80)
    
    # 测试链接列表
    test_urls = [
        # "https://weibo.com/6004371911/5233241829410136",
        # "https://weibo.com/6004371911/5233249841580953",
        # "https://m.weibo.cn/detail/5224958596222067",
        # "https://weibo.com/1566936885/QdC5HtUjg",
        "https://weibo.com/1859841950/QdV89zORJ"
    ]
    
    parser = WeiboParser()
    
    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            await test_single_url(parser, session, url)
            # 添加延迟，避免请求过快
            await asyncio.sleep(1)
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

