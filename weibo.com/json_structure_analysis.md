# 微博 JSON 返回数据结构分析
> https://weibo.com/2476177283/5232630992732508

---

## 一、基本信息 (Basic Info)

### 1.1 微博标识
- **`id`**: `5232630992732508` - 微博唯一数字 ID
- **`idstr`**: `"5232630992732508"` - 微博 ID 字符串形式
- **`mid`**: `"5232630992732508"` - 微博 MID
- **`mblogid`**: `"QdGSDbsQI"` - 微博短 ID

### 1.2 时间信息
- **`created_at`**: `"Thu Nov 13 21:18:29 +0800 2025"` - 创建时间（GMT+8）

### 1.3 文本内容
- **`text`**: `"这就是漫展的魅力吧！ \u200b\u200b\u200b"` - 显示文本（HTML 转义）
- **`text_raw`**: `"这就是漫展的魅力吧！ \u200b\u200b\u200b"` - 原始文本
- **`textLength`**: `20` - 文本长度

### 1.4 发布信息
- **`source`**: `"iPhone 15"` - 发布来源设备
- **`region_name`**: `"发布于 安徽"` - 发布地区

---

## 二、用户信息 (User Info)

### 2.1 用户基本信息
- **`user.id`**: `2476177283` - 用户 ID
- **`user.screen_name`**: `"春天的两只虫·"` - 用户昵称
- **`user.verified`**: `True` - 是否认证
- **`user.verified_type`**: `0` - 认证类型
- **`user.verified_type_ext`**: `2` - 扩展认证类型

### 2.2 用户头像
- **`user.profile_image_url`**: 50x50 头像
- **`user.avatar_large`**: 180x180 大头像
- **`user.avatar_hd`**: 1024x1024 高清头像

### 2.3 用户统计
- **`user.status_total_counter`**: 用户总数据统计
  - `total_cnt_format`: `"18万"` - 总互动数（格式化）
  - `comment_cnt`: `"23,337"` - 评论数
  - `repost_cnt`: `"3,855"` - 转发数
  - `like_cnt`: `"152,460"` - 点赞数
  - `total_cnt`: `"179,652"` - 总互动数（数字）

### 2.4 用户 VIP 信息
- **`user.mbrank`**: `1` - 会员等级
- **`user.mbtype`**: `12` - 会员类型
- **`user.icon_list`**: VIP 图标列表

---

## 三、图片信息 (Picture Info)

### 3.1 图片列表
- **`pic_ids`**: `['93977783ly1i7aw53lly8g20qo0f01ln', '93977783ly1i7aw4w4i87g20qo0f07x7']` - 图片 ID 列表
- **`pic_num`**: `2` - 图片数量

### 3.2 图片详细信息 (`pic_infos`)

每个图片对象包含以下信息：

#### 3.2.1 多尺寸图片链接
- **`thumbnail`**: 180x101 - 缩略图
- **`bmiddle`**: 360x202 - 中等尺寸
- **`large`**: 960x540 - 大图
- **`original`**: 960x540 - 原图
- **`largest`**: 960x540 - 最大尺寸（**推荐下载此尺寸**）
- **`mw2000`**: 960x540 - 最大宽度 2000
- **`largecover`**: 960x540 - 大封面

#### 3.2.2 图片元数据
- **`pic_id`**: 图片唯一 ID
- **`type`**: `"gif"` - 图片类型（GIF 动图）
- **`photo_tag`**: `0` - 图片标签
- **`pic_status`**: `1` - 图片状态
- **`object_id`**: 对象 ID
- **`width`**: `960` - 宽度
- **`height`**: `540` - 高度
- **`cut_type`**: `1` - 裁剪类型

#### 3.2.3 GIF 视频信息（重要！）
- **`video`**: GIF 动图对应的 MP4 视频链接
  - 格式：`http://g.us.sinaimg.cn/o0/xxx.mp4?label=gif_mp4&template=960x540.28.0&...`
  - **这是 GIF 的 MP4 版本，文件更小，质量更好，推荐下载**
- **`video_object_id`**: `"1022:2311285232630992666651"` - 视频对象 ID

---

## 四、互动数据 (Engagement Data)

- **`reposts_count`**: `6` - 转发数
- **`comments_count`**: `24` - 评论数
- **`attitudes_count`**: `305` - 点赞数
- **`favorited`**: `False` - 是否已收藏

---

## 五、权限与可见性 (Privacy & Visibility)

- **`visible.type`**: `0` - 可见性类型
- **`visible.list_id`**: `0` - 可见列表 ID
- **`title.text`**: `"公开"` - 可见性标题
- **`can_edit`**: `False` - 是否可编辑
- **`content_auth`**: `0` - 内容权限

---

## 六、评论管理 (Comment Management)

- **`comment_manage_info`**:
  - `comment_permission_type`: `-1` - 评论权限类型
  - `approval_comment_type`: `0` - 评论审核类型
  - `comment_sort_type`: `0` - 评论排序类型

---

## 七、其他元数据 (Other Metadata)

- **`is_paid`**: `False` - 是否付费内容
- **`isLongText`**: `False` - 是否长文本
- **`mblogtype`**: `0` - 微博类型
- **`isAd`**: `False` - 是否广告
- **`ok`**: `1` - 请求状态（1=成功）
- **`cardid`**: `"raresvip_0032000828"` - 卡片 ID
- **`pic_bg_new`**: VIP 背景图片 URL
- **`mblog_vip_type`**: `0` - VIP 微博类型

---

## 八、数据展示策略

- **`number_display_strategy`**: 数字显示策略
  - `display_text`: `"100万+"` - 显示文本
  - `display_text_min_number`: `1000000` - 最小显示数字

---

## 关键发现

### 1. GIF 动图处理
这个微博包含的是 **GIF 动图**，但微博实际上存储为 **MP4 视频格式**：
- 每个 GIF 都有对应的 `video` 字段，包含 MP4 链接
- MP4 格式文件更小，质量更好
- **建议下载 MP4 版本而不是 GIF 版本**

### 2. 图片下载优先级
1. **首选**: `largest.url` - 最大尺寸图片
2. **GIF 动图**: `video` - MP4 视频版本（更优）
3. **备选**: `original.url` - 原图

### 3. 数据结构特点
- `pic_infos` 是一个字典，key 是 `pic_id`，value 是图片详细信息
- 每个图片都有多种尺寸的 URL
- GIF 类型图片会额外包含 `video` 字段

---

## 建议的提取逻辑

```python
# 对于 GIF 图片，优先下载 MP4 视频
if pic_info.get('type') == 'gif' and pic_info.get('video'):
    # 下载 MP4 视频
    download_url = pic_info['video']
    file_ext = '.mp4'
else:
    # 下载最大尺寸图片
    download_url = pic_info['largest']['url']
    file_ext = '.gif' if pic_info.get('type') == 'gif' else '.jpg'
```

