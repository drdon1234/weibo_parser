### 请求步骤

1. 从原始url中提取视频id（1034:5233218052358208）：https://video.weibo.com/show?fid=1034:5233218052358208

2. 获取post请求头必要参数：
发送post请求（.gen_visitor_cookie.py），生成访客cookie，获取"SUB"参数

3. 发送post请求(get_json.py)（请求头必须携带cookie中的"SUB"参数和作为referer的第一次重定向url，载荷根据第1步获取的视频id拼装：'data': '{"Component_Play_Playinfo":{"oid":"1034:5233218052358208"}}'）
获取json类型的网页数据：
https://weibo.com/tv/api/component?page=/tv/show/1034:5233218052358208
获取页面内最高画质的视频直链，比如该视频页的：response.txt 中的 "高清 1080P": "//f.video.weibocdn.com/o0/zEisketGlx08sZESDxHy010412006kml0E010.mp4?label=mp4_1080p&template=1920x1080.25.0&media_id=5233218052358208&tp=8x8A3El:YTkl0eM8&us=0&ori=1&bf=4&ot=h&ps=3lckmu&uid=3ZoTIp&ab=,15568-g4,8012-g2,3601-g43,8013-g0&Expires=1763184834&ssig=FbXEoU3VOO&KID=unistore,video"

4. 下载媒体
