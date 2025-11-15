# 微博视频 JSON 返回数据结构分析
> https://video.weibo.com/show?fid=1034:5233218052358208

---

## 一、基本信息 (Basic Info)

### 1.1 响应状态
- **`code`**: `"100000"` - 响应代码（100000 表示成功）
- **`msg`**: `"succ"` - 响应消息

### 1.2 视频标识
- **`id`**: `"1034:5233218052358208"` - 视频 ID（格式：类型:ID）
- **`oid`**: `"1034:5233218052358208"` - 对象 ID
- **`media_id`**: `5233218052358208` - 媒体 ID（数字）
- **`mid`**: `5233210469909717` - 微博 MID
- **`idstr`**: `"1034:5233218052358208"` - ID 字符串形式

### 1.3 时间信息
- **`date`**: `"23分钟前"` - 相对时间（格式化显示）
- **`real_date`**: `1763179875` - 真实时间戳（Unix 时间戳）

### 1.4 文本内容
- **`title`**: `"星探长的微博视频"` - 视频标题
- **`text`**: HTML 格式的文本内容（包含话题标签等）

---

## 二、用户信息 (User Info)

### 2.1 用户基本信息
- **`author`**: `"星探长"` - 作者昵称
- **`nickname`**: `"星探长"` - 用户昵称
- **`author_id`**: `6468005444` - 作者 ID
- **`user.id`**: `6468005444` - 用户 ID
- **`verified`**: `true` - 是否认证
- **`verified_type`**: `0` - 认证类型
- **`verified_type_ext`**: `1` - 扩展认证类型
- **`verified_reason`**: `"综艺博主"` - 认证原因

### 2.2 用户头像
- **`avatar`**: 小头像 URL（相对路径，需补全协议）

### 2.3 用户统计
- **`followers_count`**: `"1193.2万"` - 粉丝数（格式化）
- **`reposts_count`**: `"21"` - 转发数
- **`comments_count`**: `"86"` - 评论数
- **`attitudes_count`**: `1144` - 点赞数

---

## 三、视频信息 (Video Info)

### 3.1 视频链接 (`urls`)

视频链接存储在 `urls` 对象中，包含多个清晰度选项：

- **`"高清 1080P"`**: 1080P 高清视频链接（**推荐下载此清晰度**）
  - 格式：`//f.video.weibocdn.com/o0/xxx.mp4?label=mp4_1080p&template=1920x1080.25.0&...`
  - 分辨率：1920x1080
- **`"高清 720P"`**: 720P 高清视频链接
  - 分辨率：1280x720
- **`"标清 480P"`**: 480P 标清视频链接
  - 分辨率：852x480

**注意**：
- URL 以 `//` 开头，需要补全协议为 `https:`
- 清晰度一般从高到低排序（第一个通常是最清晰的）
- 建议直接选择第一个 URL

### 3.2 视频元数据
- **`cover_image`**: `"//wx1.sinaimg.cn/orj480/..."` - 封面图片（相对路径）
- **`duration`**: `"0:11"` - 视频时长（格式化显示）
- **`duration_time`**: `11.331` - 视频时长（秒，浮点数）
- **`play_start`**: `0` - 播放起始位置
- **`play_start_time`**: `0` - 播放起始时间
- **`video_orientation`**: `"horizontal"` - 视频方向（horizontal/vertical）
- **`play_count`**: `"10.3万"` - 播放次数（格式化）

### 3.3 视频流信息
- **`stream_url`**: 视频流 URL（备用链接，通常为低清晰度）

---

## 四、互动数据 (Engagement Data)

- **`reposts_count`**: `"21"` - 转发数
- **`comments_count`**: `"86"` - 评论数
- **`attitudes_count`**: `1144` - 点赞数
- **`attitude`**: `false` - 是否已点赞
- **`is_follow`**: `false` - 是否已关注

---

## 五、其他信息

### 5.1 话题标签
- **`topics`**: 话题数组
  - `content`: 话题内容，如 `"卢昱晓lv官宣"`

### 5.2 短链接
- **`url_short`**: `"http://t.cn/AX2HphsG"` - 短链接

### 5.3 评论管理
- **`comment_manage_info`**:
  - `comment_permission_type`: `-1` - 评论权限类型
  - `approval_comment_type`: `0` - 评论审核类型
  - `comment_sort_type`: `0` - 评论排序类型

### 5.4 其他元数据
- **`uuid`**: `"5233218059239844"` - UUID
- **`is_paid`**: `false` - 是否付费内容
- **`live`**: `false` - 是否直播
- **`is_show_bulletin`**: `3` - 公告显示状态
- **`object_type`**: `"video"` - 对象类型
- **`allow_comment`**: `false` - 是否允许评论
- **`ip_info_str`**: `"发布于 山西"` - IP 信息

---

## 关键发现

### 1. 视频清晰度选择
- `urls` 对象包含多个清晰度选项
- **清晰度一般从高到低排序**（第一个通常是最清晰的）
- **建议直接选择第一个 URL**，无需硬编码清晰度名称

### 2. URL 协议补全
- 所有媒体 URL 都以 `//` 开头（协议相对 URL）
- **需要补全为 `https:`** 才能正常访问

### 3. 数据结构特点
- 响应结构：`data.Component_Play_Playinfo`
- 视频链接存储在 `urls` 对象中
- 每个清晰度对应一个 URL

---

## 建议的提取逻辑

```python
# 提取视频链接
playinfo = json_data.get('data', {}).get('Component_Play_Playinfo', {})
urls = playinfo.get('urls', {})

if urls:
    # 直接选择第一个 URL（清晰度一般从高到低排序）
    video_url = list(urls.values())[0]
    
    # 如果 URL 以 // 开头，补全协议
    if video_url.startswith('//'):
        video_url = 'https:' + video_url
```

---

## 数据路径总结

- **视频链接**: `data.Component_Play_Playinfo.urls`（第一个值）
- **视频标题**: `data.Component_Play_Playinfo.title`
- **作者**: `data.Component_Play_Playinfo.author`
- **发布时间**: `data.Component_Play_Playinfo.real_date`（时间戳）
- **封面图片**: `data.Component_Play_Playinfo.cover_image`
- **视频时长**: `data.Component_Play_Playinfo.duration_time`（秒）
- **播放次数**: `data.Component_Play_Playinfo.play_count`
- **互动数据**: `data.Component_Play_Playinfo.reposts_count`、`comments_count`、`attitudes_count`

