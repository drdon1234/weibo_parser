# 微博手机短链 JSON 返回数据结构分析
> https://m.weibo.cn/detail/5221716881314113（图片示例）
> https://m.weibo.cn/detail/5224958596222067（视频示例）

---

## 一、数据获取方式

### 1.1 响应格式
- 响应为 **HTML 格式**，包含 JavaScript 变量
- JSON 数据存储在 `$render_data` 变量中
- 需要从 HTML 中提取：`var $render_data = [{...}][0] || {};`

### 1.2 提取方法
```javascript
var $render_data = [{...}][0] || {};
```
- 使用正则表达式提取：`var \$render_data = (\[.*?\])\[0\]`
- 解析 JSON 数组，取第一个元素

---

## 二、基本信息 (Basic Info)

### 2.1 微博标识
- **`status.id`**: `"5221716881314113"` - 微博唯一数字 ID
- **`status.mid`**: `"5221716881314113"` - 微博 MID
- **`status.bid`**: `"QathNq6DV"` - 微博短 ID（视频类型）

### 2.2 时间信息
- **`status.created_at`**: `"Tue Oct 14 18:29:42 +0800 2025"` - 创建时间（GMT+8）
- **`status.edit_at`**: `"Thu Oct 23 21:59:15 +0800 2025"` - 编辑时间（如果存在）

### 2.3 文本内容
- **`status.text`**: HTML 格式的文本内容（包含表情、话题标签等）
- **`status.textLength`**: `16` - 文本长度
- **`status.source`**: `""` 或 `"微博视频号"` - 发布来源

---

## 三、用户信息 (User Info)

### 3.1 用户基本信息
- **`status.user.id`**: `1669879400` - 用户 ID
- **`status.user.screen_name`**: `"Dear-迪丽热巴"` - 用户昵称
- **`status.user.verified`**: `true` - 是否认证
- **`status.user.verified_type`**: `0` - 认证类型
- **`status.user.verified_type_ext`**: `1` - 扩展认证类型
- **`status.user.verified_reason`**: `"嘉行传媒签约演员　"` - 认证原因

### 3.2 用户头像
- **`status.user.profile_image_url`**: 180x180 头像
- **`status.user.avatar_hd`**: 高清头像

### 3.3 用户统计
- **`status.user.followers_count`**: `"8181.1万"` - 粉丝数（格式化）
- **`status.user.followers_count_str`**: `"8181.1万"` - 粉丝数字符串
- **`status.user.statuses_count`**: `1840` - 微博数

---

## 四、图片信息 (Picture Info)

### 4.1 图片列表
- **`status.pic_ids`**: `['001P0DUIgy1i6c3017bq2j62c03404qs02', ...]` - 图片 ID 列表

### 4.2 图片详细信息 (`status.pics`)

每个图片对象包含以下信息：

#### 4.2.1 图片基本信息
- **`pid`**: `"001P0DUIgy1i6c3017bq2j62c03404qs02"` - 图片唯一 ID
- **`url`**: 默认尺寸图片 URL（通常是 orj360）
- **`size`**: `"orj360"` - 图片尺寸标识

#### 4.2.2 图片尺寸信息 (`geo`)
- **`geo.width`**: `360` - 宽度
- **`geo.height`**: `479` - 高度
- **`geo.croped`**: `false` - 是否裁剪

#### 4.2.3 大尺寸图片 (`large`) - **推荐下载此尺寸**
- **`large.size`**: `"large"` - 尺寸标识
- **`large.url`**: `"https://wx2.sinaimg.cn/large/001P0DUIgy1i6c3017bq2j62c03404qs02.jpg"` - **大尺寸图片 URL**
- **`large.geo.width`**: `2048` - 大图宽度
- **`large.geo.height`**: `2730` - 大图高度
- **`large.geo.croped`**: `false` - 是否裁剪

### 4.3 图片焦点信息
- **`status.pic_focus_point`**: 图片焦点位置数组（用于显示优化）

---

## 五、视频信息 (Video Info)

### 5.1 视频页面信息 (`status.page_info`)

当 `status.page_info.type == "video"` 时，包含视频信息：

#### 5.1.1 视频基本信息
- **`page_info.type`**: `"video"` - 类型标识
- **`page_info.object_type`**: `11` - 对象类型
- **`page_info.object_id`**: `"1034:5224958524326016"` - 对象 ID
- **`page_info.page_title`**: `"红莲爱科技的微博视频"` - 页面标题
- **`page_info.title`**: `""` - 标题（可能为空）
- **`page_info.content1`**: `"红莲爱科技的微博视频"` - 内容1
- **`page_info.content2`**: 视频描述文本

#### 5.1.2 视频链接 (`page_info.urls`)

视频链接存储在 `urls` 对象中，包含多个清晰度选项：

- **`"mp4_720p_mp4"`**: 720P 视频链接（**推荐下载此清晰度**）
  - 格式：`https://f.video.weibocdn.com/o0/xxx.mp4?label=mp4_720p&template=720x1280.24.0&...`
  - 分辨率：720x1280（竖屏）或 1280x720（横屏）
- **`"mp4_hd_mp4"`**: HD 视频链接
  - 分辨率：540x960（竖屏）或 960x540（横屏）
- **`"mp4_ld_mp4"`**: LD（低清）视频链接
  - 分辨率：360x640（竖屏）或 640x360（横屏）

**注意**：
- 清晰度一般从高到低排序（第一个通常是最清晰的）
- 建议直接选择第一个 URL

#### 5.1.3 视频流信息 (`page_info.media_info`)
- **`media_info.stream_url`**: 视频流 URL（低清，备用）
- **`media_info.stream_url_hd`**: 高清视频流 URL
- **`media_info.duration`**: `17.042` - 视频时长（秒，浮点数）

#### 5.1.4 视频元数据
- **`page_info.video_orientation`**: `"vertical"` - 视频方向（vertical/horizontal）
- **`page_info.play_count`**: `"265万次播放"` - 播放次数（格式化）
- **`page_info.page_pic`**: 视频封面图片信息
  - `url`: 封面图片 URL
  - `width`: 宽度
  - `height`: 高度

---

## 六、互动数据 (Engagement Data)

- **`status.reposts_count`**: `1000000` 或 `224` - 转发数
- **`status.comments_count`**: `1000000` 或 `209` - 评论数
- **`status.attitudes_count`**: `10430176` 或 `10849` - 点赞数
- **`status.favorited`**: `false` - 是否已收藏
- **`status.reprint_cmt_count`**: `0` - 转载评论数

---

## 七、其他元数据 (Other Metadata)

- **`status.is_paid`**: `false` - 是否付费内容
- **`status.isLongText`**: `false` - 是否长文本
- **`status.mblogtype`**: `0` - 微博类型
- **`status.pic_num`**: `3` 或 `1` - 图片数量
- **`status.region_name`**: `"发布于 江苏"` - 发布地区
- **`status.can_edit`**: `false` - 是否可编辑
- **`status.ok`**: `1` - 请求状态（1=成功）

---

## 关键发现

### 1. 数据提取方式
- 响应是 HTML，需要从 JavaScript 变量中提取 JSON
- 使用正则表达式：`var \$render_data = (\[.*?\])\[0\]`
- 解析后取数组的第一个元素

### 2. 图片下载优先级
1. **首选**: `status.pics[].large.url` - 大尺寸图片（最高画质）
2. **备选**: `status.pics[].url` - 默认尺寸图片

### 3. 视频下载优先级
1. **首选**: `status.page_info.urls` 的第一个值（通常是最清晰的）
2. **备选**: `status.page_info.media_info.stream_url_hd` - 高清流
3. **最后**: `status.page_info.media_info.stream_url` - 普通流

### 4. 数据结构特点
- 图片和视频信息都在 `status` 对象中
- 图片：`status.pics` 数组
- 视频：`status.page_info` 对象（当 `type == "video"` 时）

---

## 建议的提取逻辑

### 图片提取
```python
# 提取图片链接
pics = json_data.get('status', {}).get('pics', [])
for pic in pics:
    large = pic.get('large', {})
    if large:
        url = large.get('url', '')
        # url 即为最高画质的图片链接
```

### 视频提取
```python
# 提取视频链接
page_info = json_data.get('status', {}).get('page_info', {})
if page_info and page_info.get('type') == 'video':
    urls = page_info.get('urls', {})
    if urls:
        # 直接选择第一个 URL（清晰度一般从高到低排序）
        video_url = list(urls.values())[0]
        # 如果 URL 以 // 开头，补全协议
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
```

---

## 数据路径总结

### 图片类型
- **图片链接**: `status.pics[].large.url`
- **图片 ID**: `status.pic_ids[]`
- **图片数量**: `status.pic_num`

### 视频类型
- **视频链接**: `status.page_info.urls`（第一个值）
- **视频标题**: `status.page_info.page_title`
- **视频时长**: `status.page_info.media_info.duration`（秒）
- **播放次数**: `status.page_info.play_count`
- **视频方向**: `status.page_info.video_orientation`

### 通用信息
- **微博 ID**: `status.id`
- **标题/文本**: `status.text`
- **作者**: `status.user.screen_name`
- **发布时间**: `status.created_at`
- **互动数据**: `status.reposts_count`、`comments_count`、`attitudes_count`

