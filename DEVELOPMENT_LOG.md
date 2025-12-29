# 开发日志 (Development Log)

本文档记录茶话会聊天室项目的功能开发历史。

---

## 2025-12-29 - 消息撤回功能

### 功能描述
添加消息撤回功能，允许用户在发送消息后的2分钟内撤回自己的消息。

### 技术实现

#### 后端改动 (Backend Changes)

1. **数据库更新** (`backend/database.py`)
   - 在 `messages` 表中添加 `is_recalled` 字段（布尔类型，默认为0）
   - 在 `get_room_messages()` 函数中返回消息ID和撤回状态
   - 新增 `get_message()` 函数：根据消息ID获取消息详情
   - 新增 `recall_message()` 函数：将消息标记为已撤回
   - 修改 `save_message()` 函数：返回新插入消息的ID

2. **API端点** (`backend/main.py`)
   - 新增 `DELETE /api/messages/{message_id}` 端点用于撤回消息
   - 权限验证：只允许消息发送者撤回自己的消息
   - 时间限制：只允许撤回2分钟内的消息
   - 撤回后通过WebSocket广播撤回通知给房间内所有用户

3. **WebSocket更新** (`backend/main.py`)
   - 消息保存后返回消息ID，并在广播时包含ID
   - 新增 `recall` 消息类型用于通知客户端消息被撤回

#### 前端改动 (Frontend Changes)

1. **消息处理** (`frontend/src/views/Chat.vue`)
   - WebSocket消息处理中新增 `recall` 类型处理
   - 收到撤回通知后，更新对应消息的 `is_recalled` 状态

2. **UI更新** (`frontend/src/views/Chat.vue`)
   - 已撤回的消息显示为"消息已撤回"（灰色斜体）
   - 用户自己的消息显示"撤回"按钮（2分钟内有效）
   - 新增 `canRecallMessage()` 函数：判断消息是否可以撤回
   - 新增 `recallMessage()` 函数：调用API撤回消息

### 功能特性

- ✅ 用户只能撤回自己发送的消息
- ✅ 撤回时间限制为2分钟
- ✅ 撤回后所有用户实时看到"消息已撤回"
- ✅ 支持游客和注册用户
- ✅ 撤回前有确认提示

### 文件修改清单

- `backend/database.py` - 数据库操作函数
- `backend/main.py` - API端点和WebSocket处理
- `frontend/src/views/Chat.vue` - 前端聊天界面

---

## 历史功能 (Previous Features)

### 2025-12-26 - 消息时间戳和图片粘贴上传
- 添加消息时间戳显示
- 支持粘贴图片直接上传

### 2025-12-26 - 房间创建时间显示
- 显示房间创建时间
- 支持时间格式化和时间差计算

### 2025-12-25 - 用户认证系统
- 实现用户注册、登录功能
- JWT token认证
- 用户资料管理

### 初始版本 - 基础聊天功能
- 创建和加入聊天室
- 实时消息发送和接收
- 文件上传（图片、视频）
- 表情选择器
- 在线用户列表
