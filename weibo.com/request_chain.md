### 请求步骤

1. 从原始url中提取博客id（5221716881314113）：https://m.weibo.cn/detail/5221716881314113

2. 获取ajax请求头必要参数：
发送post请求（.gen_visitor_cookie.py），生成访客cookie，获取"SUB"参数

3. 发送ajax请求（get_json.py）（请求头必须携带cookie中的"SUB"参数和作为referer的原始url）获取json类型的网页数据 ，获取页面内的每个视频/图片最高画质的直链：
以该微博页面（一张图片）举例，就是ajax_response.txt内的"largest"图片："https://wx1.sinaimg.cn/large/5d658f35ly1i7ab77ydnij2223334kjq.jpg"

4. 下载图片
