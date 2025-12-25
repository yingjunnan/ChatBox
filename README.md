# 💬 聊天室应用

一个基于 Vue 3 和 FastAPI 的实时聊天应用。

## ✨ 功能特性

- 👤 **用户名管理**
  - 🎲 随机生成用户名（如：快乐的熊猫123）
  - ✏️ 手动自定义用户名
  - 💾 本地持久化存储
- 🏠 **聊天室管理**
  - ➕ 创建聊天室（支持密码保护 🔒）
  - 📋 查看活跃聊天室列表
  - 🔑 直接输入房间ID加入
- 💬 **实时通讯**
  - ⚡ WebSocket 实时消息传输
  - 📝 发送文字消息
  - 😊 表情选择器
  - 🖼️ 图片上传和预览
  - 🎥 视频上传和播放
  - 👥 在线用户状态显示（实时显示聊天室人数）

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Pinia** - Vue 状态管理
- **Vue Router** - 官方路由管理器

### 后端
- **FastAPI** - 现代高性能 Web 框架
- **WebSockets** - 实时双向通信
- **SQLite** - 轻量级数据库
- **aiosqlite** - 异步 SQLite 驱动

## 🚀 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端服务运行在 `http://localhost:8000` 🌐

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端应用运行在 `http://localhost:5173` 🌐

## 🌍 部署指南

### 部署到远程服务器

#### 1️⃣ 准备服务器环境

确保服务器已安装：
- Python 3.8+
- Node.js 16+
- Nginx（可选，用于反向代理）

#### 2️⃣ 部署后端

```bash
# 上传后端代码到服务器
scp -r backend/ user@your-server:/path/to/chatbox/

# SSH 登录服务器
ssh user@your-server

# 安装依赖
cd /path/to/chatbox/backend
pip install -r requirements.txt

# 修改 main.py 中的 CORS 配置，允许前端域名访问
# origins = ["http://your-frontend-domain.com"]

# 使用 nohup 或 systemd 运行后端服务
nohup python main.py > backend.log 2>&1 &
```

**使用 systemd 管理后端服务（推荐）**

创建服务文件 `/etc/systemd/system/chatbox-backend.service`：

```ini
[Unit]
Description=Chatbox Backend Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/chatbox/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbox-backend
sudo systemctl start chatbox-backend
sudo systemctl status chatbox-backend
```

#### 3️⃣ 部署前端

```bash
# 本地构建前端
cd frontend
npm install
npm run build

# 上传构建产物到服务器
scp -r dist/ user@your-server:/path/to/chatbox/frontend/

# 配置 Nginx
sudo nano /etc/nginx/sites-available/chatbox
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/chatbox/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 上传文件访问
    location /uploads/ {
        alias /path/to/chatbox/backend/uploads/;
    }
}
```

启用站点并重启 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/chatbox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4️⃣ 配置防火墙

```bash
# 开放 HTTP 端口
sudo ufw allow 80
sudo ufw allow 443  # 如果使用 HTTPS

# 后端端口仅允许本地访问（已通过 Nginx 代理）
sudo ufw deny 8000
```

#### 5️⃣ 配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### 6️⃣ 环境变量配置

前端已配置使用环境变量，无需手动修改代码。

**开发环境**（`.env.development`）：
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

**生产环境**（`.env.production`）：
```
# 使用空字符串表示通过 nginx 代理访问
# API 请求会使用相对路径 /api/*
# WebSocket 会根据当前页面协议自动选择 ws:// 或 wss://
VITE_API_URL=
VITE_WS_URL=
```

构建生产版本：
```bash
cd frontend
npm run build
```

构建后的文件会输出到 `frontend/dist/` 目录，上传到服务器即可。

### Docker 部署（可选）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/chatbox.db:/app/chatbox.db
      - ./backend/uploads:/app/uploads
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always
```

部署命令：
```bash
docker-compose up -d
```

## 📖 使用说明

1. 🌐 打开浏览器访问前端地址
2. 👤 系统自动生成随机用户名，可点击"编辑"自定义或"随机生成"更换
3. 🏠 选择操作：
   - ➕ 创建新聊天室（可选设置密码）
   - 📋 从列表选择已有聊天室
   - 🔑 直接输入房间ID加入
4. 💬 聊天功能：
   - 📝 发送文字消息
   - 😊 选择表情
   - 📎 上传图片或视频

## 📁 项目结构

```
chatbox/
├── backend/
│   ├── main.py           # FastAPI 主应用
│   ├── database.py       # 数据库操作
│   ├── requirements.txt  # Python 依赖
│   ├── chatbox.db        # SQLite 数据库
│   └── uploads/          # 上传文件存储
└── frontend/
    ├── src/
    │   ├── views/        # 页面组件
    │   │   ├── Home.vue  # 首页（房间列表）
    │   │   └── Chat.vue  # 聊天室页面
    │   ├── stores/       # Pinia 状态管理
    │   │   └── user.js   # 用户状态（用户名）
    │   ├── router/       # Vue Router 配置
    │   ├── App.vue       # 根组件
    │   └── main.js       # 入口文件
    └── package.json      # npm 依赖
```

## 🔧 开发指引

### 架构概览

**前后端分离架构**
- 前端：Vue 3 SPA，通过 HTTP API 和 WebSocket 与后端通信
- 后端：FastAPI 提供 RESTful API 和 WebSocket 服务
- 数据库：SQLite 存储房间和消息数据

### 数据库结构

**rooms 表**
```sql
id TEXT PRIMARY KEY          -- 房间ID（8位UUID）
name TEXT NOT NULL           -- 房间名称
password TEXT                -- 房间密码（可选）
created_at TEXT NOT NULL     -- 创建时间
```

**messages 表**
```sql
id INTEGER PRIMARY KEY       -- 消息ID（自增）
room_id TEXT NOT NULL        -- 所属房间ID
username TEXT NOT NULL       -- 发送者用户名
content TEXT NOT NULL        -- 消息内容
message_type TEXT NOT NULL   -- 消息类型（text/emoji/image/video）
created_at TEXT NOT NULL     -- 发送时间
```

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rooms` | 创建聊天室 |
| GET | `/api/rooms` | 获取聊天室列表 |
| POST | `/api/rooms/join` | 验证并加入聊天室 |
| POST | `/api/upload` | 上传文件（图片/视频） |
| WS | `/ws/{room_id}` | WebSocket 连接 |

### WebSocket 消息格式

**发送消息**
```json
{
  "username": "用户名",
  "content": "消息内容或文件URL",
  "type": "text|emoji|image|video"
}
```

**接收消息**
```json
{
  "username": "用户名",
  "content": "消息内容或文件URL",
  "type": "text|emoji|image|video"
}
```

### 添加新功能

#### 1️⃣ 添加新的消息类型

**后端** (`database.py`)
- 无需修改，`message_type` 字段支持任意类型

**前端** (`Chat.vue`)
```javascript
// 1. 添加发送逻辑
async function sendNewType(content) {
  const message = {
    username: userStore.username,
    content: content,
    type: 'new_type'
  }
  ws.send(JSON.stringify(message))
}

// 2. 添加渲染逻辑（模板中）
<div v-if="msg.type === 'new_type'">
  <!-- 自定义渲染 -->
</div>
```

#### 2️⃣ 添加新的 API 端点

**后端** (`main.py`)
```python
@app.post("/api/new-endpoint")
async def new_endpoint(data: BaseModel):
    # 处理逻辑
    return {"result": "success"}
```

**前端** (对应 Vue 组件)
```javascript
async function callNewEndpoint() {
  const response = await fetch(`${API_URL}/api/new-endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ /* 数据 */ })
  })
  return await response.json()
}
```

#### 3️⃣ 添加新的数据库表

**后端** (`database.py`)
```python
async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        # 添加新表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS new_table (
                id INTEGER PRIMARY KEY,
                field TEXT NOT NULL
            )
        """)
        await db.commit()
```

#### 4️⃣ 添加新的状态管理

**前端** (`stores/`)
```javascript
// 创建新的 store 文件
import { defineStore } from 'pinia'

export const useNewStore = defineStore('new', {
  state: () => ({
    data: null
  }),
  actions: {
    updateData(newData) {
      this.data = newData
      localStorage.setItem('data', newData)
    }
  }
})
```

### 代码规范

**前端**
- 使用 Composition API (`<script setup>`)
- 组件命名：PascalCase
- 函数命名：camelCase
- 使用 Tailwind CSS 类名进行样式设置
- 状态持久化使用 localStorage

**后端**
- 遵循 FastAPI 最佳实践
- 使用 async/await 异步编程
- 数据验证使用 Pydantic BaseModel
- 错误处理使用 HTTPException

### 常见开发任务

**停止运行中的服务**
```bash
# Windows
netstat -ano | findstr ":8000"  # 查找后端进程
netstat -ano | findstr ":5173"  # 查找前端进程
taskkill /F /PID <PID>          # 终止进程
```

**清理数据库**
```bash
# 删除数据库文件重新初始化
rm backend/chatbox.db
```

**清理上传文件**
```bash
# 清空上传目录
rm -rf backend/uploads/*
```

## 🐛 调试技巧

- **前端调试**：使用 Vue DevTools 浏览器扩展
- **后端调试**：查看终端输出的 FastAPI 日志
- **WebSocket 调试**：使用浏览器开发者工具的 Network > WS 标签
- **数据库调试**：使用 SQLite 客户端工具查看 `chatbox.db`

## 📝 待办事项

- [ ] 添加消息历史记录加载
- [ ] 添加消息已读/未读状态
- [ ] 支持消息撤回功能
- [ ] 添加聊天室成员列表
- [ ] 实现私聊功能

## 📄 许可证

MIT License

---

**Happy Coding! 🎉**
