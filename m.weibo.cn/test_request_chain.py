import aiohttp
import asyncio
import json
import re
import uuid
import os
from urllib.parse import urlparse


async def get_weibo_sub():
    """获取微博访客 SUB cookie 参数"""
    url = "https://passport.weibo.com/visitor/genvisitor2"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'content-type': 'application/x-www-form-urlencoded',
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
                return sub
            else:
                raise Exception("获取 SUB cookie 失败")


def extract_blog_id(weibo_url):
    """从微博 URL 中提取博客 ID
    
    Args:
        weibo_url: 微博链接，格式如 https://m.weibo.cn/detail/5221716881314113
        
    Returns:
        博客 ID，格式如 5221716881314113
    """
    # 匹配类似 https://m.weibo.cn/detail/5221716881314113 的 URL
    match = re.search(r'/detail/(\d+)', weibo_url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"无法从 URL 中提取博客 ID: {weibo_url}")


async def fetch_weibo_data(session, blog_id, sub_cookie):
    """获取微博 JSON 数据
    
    Args:
        session: aiohttp 会话
        blog_id: 博客 ID
        sub_cookie: SUB cookie
        
    Returns:
        微博 JSON 数据（从 HTML 中提取）
    """
    url = f"https://m.weibo.cn/detail/{blog_id}"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://visitor.passport.weibo.cn/',
        'cookie': f'SUB={sub_cookie}',
    }
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            html = await response.text()
            # 从 HTML 中提取 JSON 数据
            # 查找 var $render_data = [{...}][0] || {};
            match = re.search(r'var \$render_data = (\[.*?\])\[0\]', html, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    json_data = json.loads(json_str)
                    if json_data and len(json_data) > 0:
                        return json_data[0]
                    else:
                        raise Exception("JSON 数据为空")
                except json.JSONDecodeError as e:
                    raise Exception(f"解析 JSON 失败: {str(e)}")
            else:
                raise Exception("未找到 $render_data 数据")
        else:
            text = await response.text()
            raise Exception(f"获取微博数据失败，状态码: {response.status}, 响应: {text[:200]}")


def extract_media_urls(json_data):
    """从 JSON 数据中提取所有媒体链接（图片和视频）
    
    Args:
        json_data: 微博 JSON 数据
        
    Returns:
        媒体链接列表，格式为 [(media_type, url), ...]
    """
    media_urls = []
    status = json_data.get('status', {})
    
    # 提取图片链接
    pics = status.get('pics', [])
    if pics:
        for pic in pics:
            # 获取 large 尺寸的图片 URL
            large = pic.get('large', {})
            if large:
                url = large.get('url', '')
                if url:
                    media_urls.append(('image', url))
    
    # 提取视频链接
    page_info = status.get('page_info', {})
    if page_info and page_info.get('type') == 'video':
        urls = page_info.get('urls', {})
        if urls:
            # 直接选择第一个 URL（清晰度一般从高到低排序）
            video_url = list(urls.values())[0]
            if video_url:
                # 如果 URL 以 // 开头，补全协议
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                media_urls.append(('video', video_url))
    
    return media_urls


async def download_media(media_type, url, save_dir, index):
    """下载单个媒体文件
    
    Args:
        media_type: 媒体类型（'image' 或 'video'）
        url: 媒体 URL
        save_dir: 保存目录
        index: 文件索引
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://m.weibo.cn/',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                # 获取文件扩展名
                parsed_url = urlparse(url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1]
                
                # 如果没有扩展名，根据媒体类型判断
                if not ext:
                    if media_type == 'video' or '.mp4' in url.lower():
                        ext = '.mp4'
                    else:
                        ext = '.jpg'
                
                # 生成文件名
                filename = f"{media_type}_{index:03d}{ext}"
                filepath = os.path.join(save_dir, filename)

                # 读取并保存文件
                data = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(data)

                size_mb = len(data) / (1024 * 1024)
                print(f"  ✓ 下载成功: {filename} ({len(data)} 字节, {size_mb:.2f} MB)")
                return filepath
            else:
                print(f"  ✗ 下载失败: {url}, 状态码: {response.status}")
                return None


async def download_all_media(media_urls, save_dir):
    """并发下载所有媒体文件
    
    Args:
        media_urls: 媒体链接列表，格式为 [(media_type, url), ...]
        save_dir: 保存目录
    """
    if not media_urls:
        print("未找到媒体文件")
        return

    # 确保保存目录存在
    os.makedirs(save_dir, exist_ok=True)

    print(f"\n找到 {len(media_urls)} 个媒体文件，开始下载...")
    
    tasks = []
    for index, (media_type, url) in enumerate(media_urls, 1):
        task = download_media(media_type, url, save_dir, index)
        tasks.append(task)

    await asyncio.gather(*tasks)
    print(f"\n所有媒体文件已保存到: {save_dir}")


async def main():
    """主函数"""
    print("=" * 60)
    print("微博手机短链媒体下载工具")
    print("=" * 60)
    
    # 获取用户输入的 URL
    weibo_url = input("\n请输入微博手机短链 URL: ").strip()
    
    if not weibo_url:
        print("错误: URL 不能为空")
        return

    try:
        # 步骤 1: 提取博客 ID
        print("\n[步骤 1] 提取博客 ID...")
        blog_id = extract_blog_id(weibo_url)
        print(f"  博客 ID: {blog_id}")

        async with aiohttp.ClientSession() as session:
            # 步骤 2: 获取 SUB cookie
            print("\n[步骤 2] 获取访客 Cookie...")
            sub_cookie = await get_weibo_sub()
            print(f"  SUB Cookie: {sub_cookie[:50]}...")

            # 步骤 3: 获取微博数据
            print("\n[步骤 3] 获取微博数据...")
            json_data = await fetch_weibo_data(session, blog_id, sub_cookie)
            print("  数据获取成功")

            # 步骤 4: 提取媒体链接
            print("\n[步骤 4] 提取媒体链接...")
            media_urls = extract_media_urls(json_data)
            if not media_urls:
                print("  未找到媒体文件")
                return
            
            print(f"  找到 {len(media_urls)} 个媒体文件:")
            for i, (media_type, url) in enumerate(media_urls, 1):
                print(f"    {i}. [{media_type}] {url[:80]}...")

            # 步骤 5: 下载媒体文件
            print("\n[步骤 5] 下载媒体文件...")
            save_dir = f"downloads_{blog_id}"
            await download_all_media(media_urls, save_dir)

            print("\n" + "=" * 60)
            print("完成！")
            print("=" * 60)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

