# -*- coding: utf-8 -*-
"""
微博解析器
继承自 BaseVideoParser，实现微博链接的解析功能
"""
import re
import json
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import aiohttp

from base_parser import BaseVideoParser


class WeiboParser(BaseVideoParser):
    """微博解析器"""

    # URL匹配模式（统一管理，避免重复定义）
    URL_PATTERNS = {
        'weibo_com': [
            r'weibo\.com/\d+/[A-Za-z0-9]+',
            r'weibo\.cn/status/\d+',
        ],
        'm_weibo_cn': [
            r'm\.weibo\.cn/detail/\d+',
        ],
        'video_weibo': [
            r'video\.weibo\.com/show\?fid=',
            r'weibo\.com/tv/show/',
        ],
    }

    def __init__(self):
        """初始化微博解析器"""
        super().__init__("weibo")

    def can_parse(self, url: str) -> bool:
        """判断是否可以解析此URL
        
        Args:
            url: 微博链接
            
        Returns:
            如果是微博链接返回True，否则返回False
        """
        all_patterns = []
        for patterns in self.URL_PATTERNS.values():
            all_patterns.extend(patterns)
        return any(re.search(pattern, url) for pattern in all_patterns)

    def extract_links(self, text: str) -> List[str]:
        """从文本中提取微博链接
        
        Args:
            text: 输入文本
            
        Returns:
            提取到的微博链接列表
        """
        patterns = [
            r'https?://weibo\.com/\d+/[A-Za-z0-9]+',
            r'https?://weibo\.cn/status/\d+',
            r'https?://m\.weibo\.cn/detail/\d+',
            r'https?://video\.weibo\.com/show\?fid=[\d:]+',
            r'https?://weibo\.com/tv/show/[\d:]+',
        ]
        links = []
        for pattern in patterns:
            links.extend(re.findall(pattern, text))
        return list(set(links))

    def _get_url_type(self, url: str) -> str:
        """根据URL判断微博链接类型
        
        Args:
            url: 微博链接
            
        Returns:
            链接类型: 'weibo_com', 'm_weibo_cn', 'video_weibo'
            
        Raises:
            ValueError: 无法识别的URL类型
        """
        for url_type, patterns in self.URL_PATTERNS.items():
            if any(re.search(pattern, url) for pattern in patterns):
                return url_type
        raise ValueError(f"无法识别的URL类型: {url}")

    def _extract_page_id(self, url: str) -> str:
        """从微博 URL 中提取页面 ID
        
        支持数字ID和短ID格式：
        - 数字ID: https://weibo.com/1566936885/5232446897127970
        - 短ID: https://weibo.com/1566936885/QdC5HtUjg
        
        Args:
            url: 微博链接
            
        Returns:
            页面 ID（数字ID或短ID）
            
        Raises:
            ValueError: 无法提取页面 ID
        """
        # 匹配类似 https://weibo.com/1566936885/5232446897127970 或 https://weibo.com/1566936885/QdC5HtUjg 的 URL
        # 提取最后一个斜杠后的内容（数字或字母数字组合）
        match = re.search(r'/([A-Za-z0-9]+)$', url.rstrip('/'))
        if match:
            return match.group(1)
        else:
            raise ValueError(f"无法从 URL 中提取页面 ID: {url}")

    def _extract_blog_id(self, url: str) -> str:
        """从 m.weibo.cn URL 中提取博客 ID
        
        Args:
            url: m.weibo.cn 链接
            
        Returns:
            博客 ID
            
        Raises:
            ValueError: 无法提取博客 ID
        """
        match = re.search(r'/detail/(\d+)', url)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"无法从 URL 中提取博客 ID: {url}")

    def _extract_video_id(self, url: str) -> str:
        """从视频 URL 中提取视频 ID
        
        Args:
            url: 视频链接
            
        Returns:
            视频 ID，格式如 1034:5233218052358208
            
        Raises:
            ValueError: 无法提取视频 ID
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'fid' in params:
            return params['fid'][0]
        else:
            # 尝试从 URL 路径中提取
            match = re.search(r'/(\d+:\d+)', url)
            if match:
                return match.group(1)
            else:
                raise ValueError(f"无法从 URL 中提取视频 ID: {url}")

    async def _get_visitor_cookies(self, session: aiohttp.ClientSession) -> str:
        """获取微博访客cookie
        
        Args:
            session: aiohttp 会话
            
        Returns:
            完整的cookie字符串
            
        Raises:
            Exception: 获取失败
        """
        url = "https://visitor.passport.weibo.cn/visitor/genvisitor2"

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data = {'cb': 'visitor_gray_callback'}

        async with session.post(url, headers=headers, data=data) as response:
            if response.status != 200:
                raise Exception(f"获取cookie失败，状态码: {response.status}")
            
            # 获取响应中的所有cookie并格式化为字符串
            cookies = []
            for cookie in response.cookies.values():
                cookies.append(f"{cookie.key}={cookie.value}")
            
            if not cookies:
                raise Exception("获取cookie失败：响应中未包含cookie")
            
            cookie_str = '; '.join(cookies)
            
            # 检查是否有XSRF-TOKEN，如果没有则访问一次weibo.com页面获取
            if 'XSRF-TOKEN' not in cookie_str:
                # 访问weibo.com首页获取XSRF-TOKEN
                async with session.get('https://weibo.com', headers={'user-agent': headers['user-agent']}) as page_response:
                    if page_response.status == 200:
                        # 从响应cookie中获取XSRF-TOKEN
                        for cookie in page_response.cookies.values():
                            if cookie.key == 'XSRF-TOKEN':
                                cookies.append(f"{cookie.key}={cookie.value}")
                                cookie_str = '; '.join(cookies)
                                break
            
            return cookie_str

    def _format_author(self, screen_name: str, user_id: str) -> str:
        """格式化作者字段
        
        Args:
            screen_name: 用户名
            user_id: 用户ID
            
        Returns:
            格式化后的作者字符串，格式: {用户名}(uid:{uid})
        """
        if screen_name and user_id:
            return f"{screen_name}(uid:{user_id})"
        return screen_name or ''

    def _determine_media_type(self, pic_num: int, media_urls: List[str]) -> str:
        """判断媒体类型
        
        Args:
            pic_num: 图片数量
            media_urls: 媒体URL列表
            
        Returns:
            媒体类型: 'gallery', 'video', 'image'
        """
        if pic_num > 1:
            return "gallery"
        elif any('video' in u.lower() or '.mp4' in u.lower() for u in media_urls):
            return "video"
        else:
            return "image"

    def _normalize_url(self, url: str) -> str:
        """规范化URL，补全协议
        
        Args:
            url: 原始URL
            
        Returns:
            规范化后的URL
        """
        if url.startswith('//'):
            return 'https:' + url
        return url

    def _extract_video_url_from_dict(self, urls: Dict[str, str]) -> Optional[str]:
        """从URL字典中提取视频URL
        
        Args:
            urls: URL字典，键为清晰度标识，值为URL
            
        Returns:
            视频URL，如果不存在则返回None
        """
        if not urls or not isinstance(urls, dict):
            return None
        video_url = list(urls.values())[0]
        return self._normalize_url(video_url) if video_url else None

    def _extract_video_url_from_media_info(self, media_info: Dict[str, Any]) -> Optional[str]:
        """从media_info中提取视频URL
        
        Args:
            media_info: 媒体信息字典
            
        Returns:
            视频URL，优先返回高清URL，如果不存在则返回普通URL
        """
        if not media_info:
            return None
        hd_url = media_info.get('hd_url') or media_info.get('stream_url_hd')
        if hd_url:
            return hd_url
        stream_url = media_info.get('stream_url')
        return stream_url if stream_url else None

    def _extract_pic_url(self, pic_data: Dict[str, Any]) -> Optional[str]:
        """从图片数据中提取URL，按优先级顺序尝试
        
        Args:
            pic_data: 图片数据字典，可能包含 largest, original, large 等字段
            
        Returns:
            图片URL，如果不存在则返回None
        """
        # 优先级：largest > original > large > url
        for key in ['largest', 'original', 'large']:
            size_info = pic_data.get(key, {})
            if isinstance(size_info, dict):
                url = size_info.get('url')
                if url:
                    return url
        return pic_data.get('url')

    def _build_result_dict(
        self,
        url: str,
        media_type: str,
        author: str,
        desc: str,
        timestamp: str,
        media_urls: List[str]
    ) -> Dict[str, Any]:
        """构建解析结果字典
        
        Args:
            url: 原始URL
            media_type: 媒体类型
            author: 作者
            desc: 描述
            timestamp: 时间戳
            media_urls: 媒体URL列表
            
        Returns:
            解析结果字典
        """
        return {
            'url': url,
            'media_type': media_type,
            'title': '',
            'author': author,
            'desc': desc,
            'timestamp': timestamp,
            'video_size': None,
            'media_urls': media_urls,
        }

    async def _parse_weibo_com(
        self,
        session: aiohttp.ClientSession,
        url: str,
        cookies: str
    ) -> Dict[str, Any]:
        """解析 weibo.com 链接
        
        Args:
            session: aiohttp 会话
            url: 微博链接
            cookies: cookie 字符串
            
        Returns:
            解析结果字典
            
        Raises:
            Exception: 解析失败
        """
        page_id = self._extract_page_id(url)
        
        # 根据抓包结果，短ID和数字ID都使用id参数，并添加locale和isGetLongText参数
        api_url = f"https://weibo.com/ajax/statuses/show?id={page_id}&locale=zh-CN&isGetLongText=true"
        
        # 从cookie中提取XSRF-TOKEN（如果存在）
        xsrf_token = None
        for cookie_item in cookies.split('; '):
            if cookie_item.startswith('XSRF-TOKEN='):
                xsrf_token = cookie_item.split('=', 1)[1]
                break
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'referer': url,
            'cookie': cookies,
            'accept': 'application/json, text/plain, */*',
            'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        
        # 如果存在XSRF-TOKEN，添加到请求头
        if xsrf_token:
            headers['x-xsrf-token'] = xsrf_token

        async with session.get(api_url, headers=headers) as response:
            if response.status == 200:
                json_data = await response.json()
                
                # 检查API是否返回错误
                if json_data.get('ok') == 0:
                    error_msg = json_data.get('msg', '未知错误')
                    raise Exception(f"获取微博数据失败: {error_msg}")
                
                # 检查返回数据的结构，可能数据在data字段中
                if 'data' in json_data and isinstance(json_data['data'], dict):
                    json_data = json_data['data']
                
                media_urls = self._extract_media_urls(json_data)
                
                if not media_urls:
                    raise Exception("未找到媒体文件")
                
                user = json_data.get('user', {})
                pic_num = json_data.get('pic_num', 0)
                media_type = self._determine_media_type(pic_num, media_urls)
                
                created_at = json_data.get('created_at', '')
                formatted_timestamp = self._format_timestamp(created_at)
                
                raw_text = json_data.get('text_raw', '') or json_data.get('text', '')
                clean_text = self._clean_html_text(raw_text)
                
                screen_name = user.get('screen_name', '')
                user_id = user.get('id', '')
                author = self._format_author(screen_name, user_id)
                
                return self._build_result_dict(
                    url, media_type, author, clean_text, formatted_timestamp, media_urls
                )
            else:
                text = await response.text()
                raise Exception(f"获取微博数据失败，状态码: {response.status}, 响应: {text}")

    async def _parse_m_weibo_cn(
        self,
        session: aiohttp.ClientSession,
        url: str,
        cookies: str
    ) -> Dict[str, Any]:
        """解析 m.weibo.cn 链接
        
        Args:
            session: aiohttp 会话
            url: m.weibo.cn 链接
            cookies: cookie 字符串
            
        Returns:
            解析结果字典
            
        Raises:
            Exception: 解析失败
        """
        blog_id = self._extract_blog_id(url)
        detail_url = f"https://m.weibo.cn/detail/{blog_id}"
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'referer': 'https://visitor.passport.weibo.cn/',
            'cookie': cookies,
        }
        
        async with session.get(detail_url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                # 从 HTML 中提取 JSON 数据
                match = re.search(r'var \$render_data = (\[.*?\])\[0\]', html, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        json_data = json.loads(json_str)
                        if json_data and len(json_data) > 0:
                            status_data = json_data[0]
                            media_urls = self._extract_media_urls_m_weibo(status_data)
                            
                            if not media_urls:
                                raise Exception("未找到媒体文件")
                            
                            status = status_data.get('status', {})
                            user = status.get('user', {})
                            pic_num = len(status.get('pics', []))
                            media_type = self._determine_media_type(pic_num, media_urls)
                            
                            created_at = status.get('created_at', '')
                            formatted_timestamp = self._format_timestamp(created_at)
                            
                            raw_text = status.get('text_raw', '') or status.get('text', '')
                            clean_text = self._clean_html_text(raw_text)
                            
                            screen_name = user.get('screen_name', '')
                            user_id = user.get('id', '')
                            author = self._format_author(screen_name, user_id)
                            
                            return self._build_result_dict(
                                url, media_type, author, clean_text, formatted_timestamp, media_urls
                            )
                        else:
                            raise Exception("JSON 数据为空")
                    except json.JSONDecodeError as e:
                        raise Exception(f"解析 JSON 失败: {str(e)}")
                else:
                    raise Exception("未找到 $render_data 数据")
            else:
                text = await response.text()
                raise Exception(f"获取微博数据失败，状态码: {response.status}, 响应: {text[:200]}")

    async def _parse_video_weibo(
        self,
        session: aiohttp.ClientSession,
        url: str,
        cookies: str
    ) -> Dict[str, Any]:
        """解析 video.weibo.com 链接
        
        Args:
            session: aiohttp 会话
            url: 视频链接
            cookies: cookie 字符串
            
        Returns:
            解析结果字典
            
        Raises:
            Exception: 解析失败
        """
        video_id = self._extract_video_id(url)
        referer_url = f"https://weibo.com/tv/show/{video_id}?from=old_pc_videoshow"
        api_url = f"https://weibo.com/tv/api/component?page=/tv/show/{video_id}"
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'referer': referer_url,
            'cookie': cookies,
            'content-type': 'application/x-www-form-urlencoded',
        }
        
        payload = {
            'data': json.dumps({"Component_Play_Playinfo": {"oid": video_id}})
        }
        
        async with session.post(api_url, headers=headers, data=payload) as response:
            if response.status == 200:
                json_data = await response.json()
                media_urls = self._extract_media_urls_video(json_data)
                
                if not media_urls:
                    raise Exception("未找到视频文件")
                
                playinfo = json_data.get('data', {}).get('Component_Play_Playinfo', {})
                desc = playinfo.get('title', '') or playinfo.get('content1', '')
                screen_name = playinfo.get('author', '') or playinfo.get('author_name', '')
                user_id = playinfo.get('author_id', '') or playinfo.get('user', {}).get('id', '')
                author = self._format_author(screen_name, user_id)
                
                return self._build_result_dict(
                    url, 'video', author, desc, '', media_urls
                )
            else:
                text = await response.text()
                raise Exception(f"获取视频数据失败，状态码: {response.status}, 响应: {text}")

    def _extract_media_urls(self, json_data: Dict[str, Any]) -> List[str]:
        """从 JSON 数据中提取所有媒体链接（图片和视频）
        
        Args:
            json_data: 微博 JSON 数据
            
        Returns:
            媒体链接列表
        """
        media_urls = []
        
        # 方法1: 提取mix_media_info中的媒体（新格式，包含图片和视频）
        mix_media_info = json_data.get('mix_media_info', {})
        items = mix_media_info.get('items', [])
        if items:
            for item in items:
                item_type = item.get('type', '')
                data = item.get('data', {})
                
                if item_type == 'pic':
                    pic_url = self._extract_pic_url(data)
                    if pic_url:
                        media_urls.append(pic_url)
                
                elif item_type == 'video':
                    media_info = data.get('media_info', {})
                    video_url = self._extract_video_url_from_media_info(media_info)
                    if video_url:
                        media_urls.append(video_url)
        
        # 方法2: 提取图片链接（pic_infos格式 - weibo.com标准格式）
        pic_infos = json_data.get('pic_infos', {})
        if pic_infos:
            for pic_id, pic_info in pic_infos.items():
                pic_type = pic_info.get('type', '')
                
                # 对于 GIF 动图，优先使用 MP4 视频版本（文件更小，质量更好）
                if pic_type == 'gif' and pic_info.get('video'):
                    video_url = pic_info.get('video', '')
                    if video_url:
                        media_urls.append(video_url)
                        continue
                
                # 对于普通图片，获取最高画质的图片链接
                pic_url = self._extract_pic_url(pic_info)
                if pic_url:
                    media_urls.append(pic_url)
        
        # 方法3: 提取图片链接（pics数组格式 - 某些API返回格式）
        pics = json_data.get('pics', [])
        if pics:
            for pic in pics:
                pic_url = self._extract_pic_url(pic)
                if pic_url:
                    media_urls.append(pic_url)
        
        # 方法4: 提取视频链接（page_info 中的视频）
        page_info = json_data.get('page_info', {})
        if page_info:
            urls = page_info.get('urls', {})
            video_url = self._extract_video_url_from_dict(urls)
            if video_url:
                media_urls.append(video_url)
            
            media_info = page_info.get('media_info', {})
            video_url = self._extract_video_url_from_media_info(media_info)
            if video_url:
                media_urls.append(video_url)
        
        # 方法5: 检查是否有其他视频格式
        video_info = json_data.get('video_info', {})
        if video_info:
            video_url = video_info.get('video_details', {}).get('video_details', {})
            if video_url:
                # 尝试获取最高画质
                max_quality = max(video_url.keys(), key=lambda x: int(x) if x.isdigit() else 0, default=None)
                if max_quality:
                    url = video_url[max_quality].get('url', '')
                    if url:
                        media_urls.append(url)
        
        return media_urls

    def _extract_media_urls_m_weibo(self, json_data: Dict[str, Any]) -> List[str]:
        """从 m.weibo.cn JSON 数据中提取所有媒体链接
        
        Args:
            json_data: m.weibo.cn JSON 数据
            
        Returns:
            媒体链接列表
        """
        media_urls = []
        status = json_data.get('status', {})
        
        # 提取图片链接
        pics = status.get('pics', [])
        if pics:
            for pic in pics:
                pic_url = self._extract_pic_url(pic)
                if pic_url:
                    media_urls.append(pic_url)
        
        # 提取视频链接
        page_info = status.get('page_info', {})
        if page_info and page_info.get('type') == 'video':
            urls = page_info.get('urls', {})
            video_url = self._extract_video_url_from_dict(urls)
            if video_url:
                media_urls.append(video_url)
        
        return media_urls

    def _extract_media_urls_video(self, json_data: Dict[str, Any]) -> List[str]:
        """从 video.weibo.com JSON 数据中提取视频链接
        
        Args:
            json_data: video.weibo.com JSON 数据
            
        Returns:
            视频链接列表
        """
        media_urls = []
        try:
            playinfo = json_data.get('data', {}).get('Component_Play_Playinfo', {})
            urls = playinfo.get('urls', {})
            video_url = self._extract_video_url_from_dict(urls)
            if video_url:
                media_urls.append(video_url)
        except Exception:
            pass
        
        return media_urls

    def _clean_html_text(self, html_text: str) -> str:
        """清理HTML标签，提取纯文本
        
        处理可跳转标签（如话题标签、视频链接等），提取其中的文本内容
        
        Args:
            html_text: 包含HTML标签的文本
            
        Returns:
            清理后的纯文本
        """
        if not html_text:
            return ""
        
        text = html_text
        
        # 先提取所有 <span class="surl-text"> 的内容（话题标签和链接文本）
        # 例如: <a><span class="surl-text">#刘亦菲 今茜是何年#</span></a> -> #刘亦菲 今茜是何年#
        # 或者: <span class="surl-text">红莲爱科技的微博视频</span> -> 红莲爱科技的微博视频
        def replace_surl_text(match):
            """替换函数，提取 surl-text 内容"""
            return match.group(1)
        
        text = re.sub(
            r'<span\s+class=["\']surl-text["\']>(.*?)</span>',
            replace_surl_text,
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 移除表情图片标签 <span class="url-icon"> 及其内容
        text = re.sub(r'<span\s+class=["\']url-icon["\'][^>]*>.*?</span>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除所有 <img> 标签
        text = re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)
        
        # 将 <br /> 和 <br> 替换为空格
        text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
        
        # 移除所有剩余的HTML标签（包括 <a> 标签）
        text = re.sub(r'<[^>]+>', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def _format_timestamp(self, created_at: str) -> str:
        """格式化时间为 Y-M-D 格式
        
        Args:
            created_at: 原始时间字符串，格式如 "Thu Nov 13 21:18:29 +0800 2025"
            
        Returns:
            格式化后的时间字符串，格式如 "2025-11-13"
        """
        try:
            # 解析时间字符串
            # 格式: "Thu Nov 13 21:18:29 +0800 2025"
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            # 格式化为 Y-M-D
            return dt.strftime("%Y-%m-%d")
        except Exception:
            # 如果解析失败，返回原始字符串或空字符串
            return created_at if created_at else ""

    async def parse(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """解析单个微博链接
        
        Args:
            session: aiohttp 会话
            url: 微博链接
            
        Returns:
            解析结果字典，只包含以下字段：
            - url: 原始url
            - media_type: 媒体类型 ("video", "image", "gallery")
            - title: 标题
            - author: 作者
            - desc: 简介
            - timestamp: 上传时间（Y-M-D格式）
            - video_size: 视频大小（默认为None，本项目不实现）
            - media_urls: 媒体直链列表
            
        Raises:
            Exception: 解析失败时抛出异常
        """
        # 步骤 1: 判断URL类型
        url_type = self._get_url_type(url)
        
        # 步骤 2: 获取cookie
        cookies = await self._get_visitor_cookies(session)
        
        # 步骤 3: 根据URL类型选择对应的解析方法
        if url_type == 'weibo_com':
            return await self._parse_weibo_com(session, url, cookies)
        elif url_type == 'm_weibo_cn':
            return await self._parse_m_weibo_cn(session, url, cookies)
        elif url_type == 'video_weibo':
            return await self._parse_video_weibo(session, url, cookies)
        else:
            raise ValueError(f"不支持的URL类型: {url_type}")

