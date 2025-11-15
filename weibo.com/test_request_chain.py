import aiohttp
import asyncio
import json
import re
import uuid
import os
from urllib.parse import urlparse
from pathlib import Path


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


def extract_page_id(weibo_url):
    """从微博 URL 中提取页面 ID"""
    # 匹配类似 https://weibo.com/1566936885/5232446897127970 的 URL
    match = re.search(r'/(\d+)$', weibo_url.rstrip('/'))
    if match:
        return match.group(1)
    else:
        raise ValueError(f"无法从 URL 中提取页面 ID: {weibo_url}")


async def fetch_weibo_data(page_id, sub_cookie, referer_url):
    """获取微博 JSON 数据"""
    url = f"https://weibo.com/ajax/statuses/show?id={page_id}"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': referer_url,
        'cookie': f'SUB={sub_cookie}',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                json_data = await response.json()
                return json_data
            else:
                text = await response.text()
                raise Exception(f"获取微博数据失败，状态码: {response.status}, 响应: {text}")


def extract_media_urls(json_data):
    """从 JSON 数据中提取所有媒体链接（图片和视频）"""
    media_urls = []
    
    # 提取图片链接
    pic_infos = json_data.get('pic_infos', {})
    if pic_infos:
        for pic_id, pic_info in pic_infos.items():
            pic_type = pic_info.get('type', '')
            
            # 对于 GIF 动图，优先使用 MP4 视频版本（文件更小，质量更好）
            if pic_type == 'gif' and pic_info.get('video'):
                video_url = pic_info.get('video', '')
                if video_url:
                    media_urls.append(('video', video_url))
                    continue
            
            # 对于普通图片，获取最高画质的图片链接
            largest = pic_info.get('largest', {})
            if largest:
                url = largest.get('url', '')
                if url:
                    # 根据类型判断是图片还是视频
                    media_type = 'video' if pic_type == 'gif' else 'image'
                    media_urls.append((media_type, url))
    
    # 提取视频链接
    page_info = json_data.get('page_info', {})
    if page_info:
        media_info = page_info.get('media_info', {})
        if media_info:
            # 尝试获取最高画质的视频链接
            hd_url = media_info.get('hd_url', '')
            if hd_url:
                media_urls.append(('video', hd_url))
            else:
                # 如果没有高清链接，使用普通链接
                stream_url = media_info.get('stream_url', '')
                if stream_url:
                    media_urls.append(('video', stream_url))
    
    # 检查是否有其他视频格式
    video_info = json_data.get('video_info', {})
    if video_info:
        video_url = video_info.get('video_details', {}).get('video_details', {})
        if video_url:
            # 尝试获取最高画质
            max_quality = max(video_url.keys(), key=lambda x: int(x) if x.isdigit() else 0, default=None)
            if max_quality:
                url = video_url[max_quality].get('url', '')
                if url:
                    media_urls.append(('video', url))
    
    return media_urls


async def download_media(media_type, url, save_dir, index):
    """下载单个媒体文件"""
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://weibo.com/',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                # 获取文件扩展名
                parsed_url = urlparse(url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1]
                
                # 如果没有扩展名，根据媒体类型和 URL 判断
                if not ext:
                    if media_type == 'video' or '.mp4' in url.lower():
                        ext = '.mp4'
                    elif '.gif' in url.lower():
                        ext = '.gif'
                    else:
                        ext = '.jpg'
                
                # 生成文件名
                filename = f"{media_type}_{index:03d}{ext}"
                filepath = os.path.join(save_dir, filename)

                # 读取并保存文件
                data = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(data)

                print(f"  ✓ 下载成功: {filename} ({len(data)} 字节)")
                return filepath
            else:
                print(f"  ✗ 下载失败: {url}, 状态码: {response.status}")
                return None


async def download_all_media(media_urls, save_dir):
    """并发下载所有媒体文件"""
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
    print("微博媒体下载工具")
    print("=" * 60)
    
    # 获取用户输入的 URL
    weibo_url = input("\n请输入微博 URL: ").strip()
    
    if not weibo_url:
        print("错误: URL 不能为空")
        return

    try:
        # 步骤 1: 提取页面 ID
        print("\n[步骤 1] 提取页面 ID...")
        page_id = extract_page_id(weibo_url)
        print(f"  页面 ID: {page_id}")

        # 步骤 2: 获取 SUB cookie
        print("\n[步骤 2] 获取访客 Cookie...")
        sub_cookie = await get_weibo_sub()
        print(f"  SUB Cookie: {sub_cookie[:50]}...")

        # 步骤 3: 获取微博 JSON 数据
        print("\n[步骤 3] 获取微博数据...")
        json_data = await fetch_weibo_data(page_id, sub_cookie, weibo_url)
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
        save_dir = f"downloads_{page_id}"
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

