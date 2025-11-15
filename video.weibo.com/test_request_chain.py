import aiohttp
import asyncio
import json
import re
import uuid
import os
from urllib.parse import urlparse, parse_qs


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


def extract_video_id(video_url):
    """从视频 URL 中提取视频 ID（fid 参数）
    
    Args:
        video_url: 视频链接，格式如 https://video.weibo.com/show?fid=1034:5233218052358208
        
    Returns:
        视频 ID，格式如 1034:5233218052358208
    """
    parsed = urlparse(video_url)
    params = parse_qs(parsed.query)
    
    if 'fid' in params:
        return params['fid'][0]
    else:
        # 尝试从 URL 路径中提取
        match = re.search(r'/(\d+:\d+)', video_url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"无法从 URL 中提取视频 ID: {video_url}")


def build_referer_url(video_id):
    """构建 referer URL
    
    Args:
        video_id: 视频 ID，格式如 1034:5233218052358208
        
    Returns:
        referer URL
    """
    return f"https://weibo.com/tv/show/{video_id}?from=old_pc_videoshow"


async def fetch_video_data(session, video_id, sub_cookie, referer_url):
    """获取视频 JSON 数据
    
    Args:
        session: aiohttp 会话
        video_id: 视频 ID，格式如 1034:5233218052358208
        sub_cookie: SUB cookie
        referer_url: 重定向后的 URL（作为 referer）
        
    Returns:
        视频 JSON 数据
    """
    # 构建 API URL
    api_url = f"https://weibo.com/tv/api/component?page=/tv/show/{video_id}"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': referer_url,
        'cookie': f'SUB={sub_cookie}',
        'content-type': 'application/x-www-form-urlencoded',
    }
    
    # POST 载荷
    payload = {
        'data': json.dumps({"Component_Play_Playinfo": {"oid": video_id}})
    }
    
    async with session.post(api_url, headers=headers, data=payload) as response:
        if response.status == 200:
            json_data = await response.json()
            return json_data
        else:
            text = await response.text()
            raise Exception(f"获取视频数据失败，状态码: {response.status}, 响应: {text}")


def extract_video_url(json_data):
    """从 JSON 数据中提取视频链接（选择第一个，通常是最清晰的）
    
    Args:
        json_data: 视频 JSON 数据
        
    Returns:
        视频 URL（第一个，通常是最清晰的）
    """
    try:
        playinfo = json_data.get('data', {}).get('Component_Play_Playinfo', {})
        urls = playinfo.get('urls', {})
        
        if not urls:
            raise Exception("未找到视频链接")
        
        # 直接选择第一个 URL（清晰度一般从高到低排序）
        video_url = list(urls.values())[0]
        
        # 如果 URL 以 // 开头，补全协议
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        
        return video_url
        
    except Exception as e:
        raise Exception(f"提取视频链接失败: {str(e)}")


async def download_video(video_url, save_dir, video_id):
    """下载视频文件
    
    Args:
        video_url: 视频 URL
        save_dir: 保存目录
        video_id: 视频 ID（用于生成文件名）
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'referer': 'https://weibo.com/',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(video_url, headers=headers) as response:
            if response.status == 200:
                # 获取文件扩展名
                parsed_url = urlparse(video_url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1] or '.mp4'
                
                # 生成文件名（使用视频 ID 的后半部分）
                video_id_clean = video_id.split(':')[-1] if ':' in video_id else video_id
                filename = f"video_{video_id_clean}{ext}"
                filepath = os.path.join(save_dir, filename)

                # 读取并保存文件
                print(f"  开始下载视频...")
                data = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(data)

                size_mb = len(data) / (1024 * 1024)
                print(f"  ✓ 下载成功: {filename}")
                print(f"  文件大小: {len(data)} 字节 ({size_mb:.2f} MB)")
                return filepath
            else:
                print(f"  ✗ 下载失败，状态码: {response.status}")
                return None


async def main():
    """主函数"""
    print("=" * 60)
    print("微博视频下载工具")
    print("=" * 60)
    
    # 获取用户输入的 URL
    video_url = input("\n请输入微博视频 URL: ").strip()
    
    if not video_url:
        print("错误: URL 不能为空")
        return

    try:
        # 步骤 1: 提取视频 ID
        print("\n[步骤 1] 提取视频 ID...")
        video_id = extract_video_id(video_url)
        print(f"  视频 ID: {video_id}")

        async with aiohttp.ClientSession() as session:
            # 步骤 2: 获取 SUB cookie
            print("\n[步骤 2] 获取访客 Cookie...")
            sub_cookie = await get_weibo_sub()
            print(f"  SUB Cookie: {sub_cookie[:50]}...")

            # 步骤 3: 构建 referer URL 并获取视频数据
            print("\n[步骤 3] 获取视频数据...")
            referer_url = build_referer_url(video_id)
            print(f"  Referer URL: {referer_url}")
            json_data = await fetch_video_data(session, video_id, sub_cookie, referer_url)
            print("  数据获取成功")

            # 步骤 4: 提取视频链接
            print("\n[步骤 4] 提取视频链接...")
            video_download_url = extract_video_url(json_data)
            print(f"  视频链接: {video_download_url[:100]}...")

            # 步骤 5: 下载视频
            print("\n[步骤 5] 下载视频...")
            save_dir = f"downloads_{video_id.replace(':', '_')}"
            os.makedirs(save_dir, exist_ok=True)
            await download_video(video_download_url, save_dir, video_id)

            print("\n" + "=" * 60)
            print("完成！")
            print("=" * 60)

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

