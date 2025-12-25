# 💬 聊天室应用

一个基于 Vue 3 和 FastAPI 的实时聊天应用，支持游客模式和用户认证。

## ✨ 功能特性

### 👤 用户系统
- **游客模式**
  - 🎲 随机生成用户名（如：快乐的熊猫123）
  - ✏️ 手动自定义用户名
  - 💾 本地持久化存储
- **用户认证**（JWT Token）
  - 📝 用户注册（用户名 + 密码 + 可选显示名称和邮箱）
  - 🔐 用户登录
  - 👤 个人资料编辑（显示名称、邮箱）
  - 🔑 密码修改
  - 🖼️ 头像上传
  - 🔄 自动 Token 刷新（24小时有效期）
  - 📜 聊天记录关联到用户账户

### 🏠 聊天室管理
- ➕ 创建聊天室（支持密码保护 🔒）
- 📋 查看活跃聊天室列表
- 🔑 直接输入房间ID加入
- 👥 实时显示在线用户数量

### 💬 实时通讯
- ⚡ WebSocket 实时消息传输
- 📝 发送文字消息
- 😊 表情选择器（300+ 表情，分类显示）
- 🖼️ 图片上传和预览（点击放大）
- 🎥 视频上传和播放
- 📜 自动加载历史消息（最近100条）
- 🔔 新消息声音提醒
- 👥 在线用户状态显示

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
- **JWT (python-jose)** - Token 认证
- **bcrypt (passlib)** - 密码加密
- **python-dotenv** - 环境变量管理

## 🚀 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（首次运行）
# 复制 .env 文件并修改 JWT_SECRET_KEY
cp .env.example .env

# 启动服务
python main.py
```

后端服务运行在 `http://localhost:8000` 🌐

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用运行在 `http://localhost:5173` 🌐

## 🔐 环境变量配置

### 后端环境变量

创建 `backend/.env` 文件：

```env
# JWT 配置
JWT_SECRET_KEY=your-secret-key-here  # 使用强随机密钥
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440     # 24小时
REFRESH_TOKEN_EXPIRE_DAYS=30         # 30天
```

**生成安全的 JWT 密钥：**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 前端环境变量

**开发环境**（`.env.development`）：
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

**生产环境**（`.env.production`）：
```env
# 使用空字符串表示通过 nginx 代理访问
VITE_API_URL=
VITE_WS_URL=
```

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

# 配置环境变量
nano .env
# 设置 JWT_SECRET_KEY 为强随机密钥

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
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

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
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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
        proxy_read_timeout 86400;
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

#### 6️⃣ 数据库备份

定期备份 SQLite 数据库：

```bash
# 创建备份脚本
cat > /path/to/chatbox/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/chatbox/backend/chatbox.db "$BACKUP_DIR/chatbox_$DATE.db"
# 保留最近7天的备份
find "$BACKUP_DIR" -name "chatbox_*.db" -mtime +7 -delete
EOF

chmod +x /path/to/chatbox/backup.sh

# 添加到 crontab（每天凌晨2点备份）
crontab -e
# 添加：0 2 * * * /path/to/chatbox/backup.sh
```

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
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=1440
      - REFRESH_TOKEN_EXPIRE_DAYS=30
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

### 游客模式
1. 🌐 打开浏览器访问前端地址
2. 👤 系统自动生成随机用户名，可点击"编辑"自定义或"随机生成"更换
3. 🏠 选择操作：
   - ➕ 创建新聊天室（可选设置密码）
   - 📋 从列表选择已有聊天室
   - 🔑 直接输入房间ID加入
4. 💬 聊天功能：
   - 📝 发送文字消息
   - 😊 选择表情（300+ 表情）
   - 📎 上传图片或视频

### 注册/登录
1. 点击首页的"登录 / 注册账号"按钮
2. 选择"注册"标签，填写：
   - 用户名（必填，唯一）
   - 密码（必填，至少6个字符）
   - 显示名称（可选）
   - 邮箱（可选）
3. 或选择"登录"标签，使用已有账号登录

### 登录用户功能
- 📝 编辑个人资料（显示名称、邮箱）
- 🔑 修改密码
- 🖼️ 上传头像
- 📜 查看聊天历史（自动加载）
- 💾 用户名和资料永久保存

## 📁 项目结构

```
chatbox/
├── backend/
│   ├── main.py              # FastAPI 主应用
│   ├── database.py          # 数据库操作
│   ├── auth.py              # JWT 认证和密码加密
│   ├── crud.py              # 用户 CRUD 操作
│   ├── models.py            # Pydantic 数据模型
│   ├── dependencies.py      # FastAPI 依赖注入
│   ├── config.py            # 配置管理
│   ├── .env                 # 环境变量（需创建）
│   ├── requirements.txt     # Python 依赖
│   ├── chatbox.db           # SQLite 数据库
│   └── uploads/             # 上传文件存储
└── frontend/
    ├── src/
    │   ├── views/           # 页面组件
    │   │   ├── Home.vue     # 首页（房间列表）
    │   │   └── Chat.vue     # 聊天室页面
    │   ├── components/      # 可复用组件
    │   │   ├── AuthModal.vue         # 登录/注册模态框
    │   │   └── ProfileEditModal.vue  # 资料编辑模态框
    │   ├── stores/          # Pinia 状态管理
    │   │   └── user.js      # 用户状态（游客/认证）
    │   ├── router/          # Vue Router 配置
    │   ├── App.vue          # 根组件
    │   └── main.js          # 入口文件
    └── package.json         # npm 依赖
```

## 🔧 开发指引

### 架构概览

**前后端分离架构**
- 前端：Vue 3 SPA，通过 HTTP API 和 WebSocket 与后端通信
- 后端：FastAPI 提供 RESTful API 和 WebSocket 服务
- 数据库：SQLite 存储房间、消息和用户数据
- 认证：JWT Token（Access Token + Refresh Token）

### 数据库结构

**users 表**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
username TEXT UNIQUE NOT NULL       -- 用户名（唯一）
password_hash TEXT NOT NULL         -- 密码哈希（bcrypt）
display_name TEXT                   -- 显示名称
email TEXT                          -- 邮箱
avatar_url TEXT                     -- 头像URL
created_at TEXT NOT NULL            -- 创建时间
updated_at TEXT NOT NULL            -- 更新时间
```

**refresh_tokens 表**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id INTEGER NOT NULL            -- 用户ID
token TEXT UNIQUE NOT NULL          -- Refresh Token
expires_at TEXT NOT NULL            -- 过期时间
created_at TEXT NOT NULL            -- 创建时间
FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
```

**rooms 表**
```sql
id TEXT PRIMARY KEY                 -- 房间ID（8位UUID）
name TEXT NOT NULL                  -- 房间名称
password TEXT                       -- 房间密码（可选）
created_at TEXT NOT NULL            -- 创建时间
owner_id INTEGER                    -- 创建者ID（可选）
is_private BOOLEAN DEFAULT 0        -- 是否私密
```

**messages 表**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
room_id TEXT NOT NULL               -- 所属房间ID
username TEXT NOT NULL              -- 发送者用户名/显示名称
content TEXT NOT NULL               -- 消息内容
message_type TEXT NOT NULL          -- 消息类型（text/emoji/image/video）
created_at TEXT NOT NULL            -- 发送时间
user_id INTEGER                     -- 用户ID（登录用户）
is_guest BOOLEAN DEFAULT 1          -- 是否游客
FOREIGN KEY (room_id) REFERENCES rooms (id)
```

### API 端点

#### 认证相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/refresh` | 刷新 Access Token |
| POST | `/api/auth/logout` | 登出（删除 Refresh Token） |

#### 用户相关
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/me` | 获取当前用户信息 |
| PUT | `/api/users/me` | 更新用户资料 |
| POST | `/api/users/me/avatar` | 上传头像 |
| POST | `/api/users/me/password` | 修改密码 |

#### 聊天室相关
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rooms` | 创建聊天室 |
| GET | `/api/rooms` | 获取聊天室列表 |
| POST | `/api/rooms/join` | 验证并加入聊天室 |
| GET | `/api/rooms/{room_id}/messages` | 获取房间历史消息 |

#### 文件上传
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传文件（图片/视频） |

#### WebSocket
| 协议 | 路径 | 说明 |
|------|------|------|
| WS | `/ws/{room_id}?username=xxx` | 游客连接 |
| WS | `/ws/{room_id}?token=xxx` | 认证用户连接 |

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

**系统消息（加入/离开）**
```json
{
  "type": "system",
  "action": "join|leave",
  "username": "用户名",
  "online_users": ["用户1", "用户2"]
}
```

### 认证流程

#### 注册/登录
1. 用户提交用户名和密码
2. 后端验证并生成 Access Token（24小时）和 Refresh Token（30天）
3. 前端保存 tokens 到 localStorage
4. 前端使用 Access Token 访问受保护的 API

#### Token 刷新
1. Access Token 过期时，API 返回 401
2. 前端自动使用 Refresh Token 请求新的 Access Token
3. 刷新成功后重试原请求
4. 刷新失败则清除认证状态，切换到游客模式

#### WebSocket 认证
- 游客：`/ws/{room_id}?username=xxx`
- 登录用户：`/ws/{room_id}?token=xxx`（后端自动解析用户信息）

### 添加新功能

#### 1️⃣ 添加新的消息类型

**后端** (`database.py`)
- 无需修改，`message_type` 字段支持任意类型

**前端** (`Chat.vue`)
```javascript
// 1. 添加发送逻辑
async function sendNewType(content) {
  const message = {
    username: userStore.displayName || userStore.username,
    content: content,
    type: 'new_type'
  }
  ws.value.send(JSON.stringify(message))
}

// 2. 添加渲染逻辑（模板中）
<div v-if="msg.type === 'new_type'">
  <!-- 自定义渲染 -->
</div>
```

#### 2️⃣ 添加新的 API 端点

**后端** (`main.py`)
```python
from dependencies import get_current_user

@app.post("/api/new-endpoint")
async def new_endpoint(data: BaseModel, current_user: User = Depends(get_current_user)):
    # 需要认证的端点
    return {"result": "success"}

@app.get("/api/public-endpoint")
async def public_endpoint():
    # 公开端点
    return {"result": "success"}
```

**前端** (对应 Vue 组件)
```javascript
// 需要认证的请求
async function callAuthEndpoint() {
  const response = await fetch(`${API_URL}/api/new-endpoint`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userStore.accessToken}`
    },
    body: JSON.stringify({ /* 数据 */ })
  })

  // 处理 401 错误（token 过期）
  if (response.status === 401) {
    const refreshed = await userStore.refreshAccessToken()
    if (refreshed) {
      // 重试请求
    }
  }

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
      localStorage.setItem('data', JSON.stringify(newData))
    },
    loadData() {
      const saved = localStorage.getItem('data')
      if (saved) {
        this.data = JSON.parse(saved)
      }
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
- 敏感数据（tokens）存储在 localStorage，页面刷新时自动恢复

**后端**
- 遵循 FastAPI 最佳实践
- 使用 async/await 异步编程
- 数据验证使用 Pydantic BaseModel
- 错误处理使用 HTTPException
- 密码使用 bcrypt 加密，不存储明文
- JWT 密钥存储在环境变量中

### 常见开发任务

**停止运行中的服务**
```bash
# Windows
netstat -ano | findstr ":8000"  # 查找后端进程
netstat -ano | findstr ":5173"  # 查找前端进程
taskkill /F /PID <PID>          # 终止进程

# Linux/Mac
lsof -ti:8000 | xargs kill -9   # 终止后端
lsof -ti:5173 | xargs kill -9   # 终止前端
```

**清理数据库**
```bash
# 删除数据库文件重新初始化
rm backend/chatbox.db
# 重启后端服务，数据库会自动重建
```

**清理上传文件**
```bash
# 清空上传目录
rm -rf backend/uploads/*
mkdir backend/uploads
```

**重置用户密码（管理员操作）**
```python
# 在 Python 环境中执行
import asyncio
from auth import hash_password
from crud import get_user_by_username
import aiosqlite

async def reset_password(username, new_password):
    async with aiosqlite.connect("chatbox.db") as db:
        password_hash = hash_password(new_password)
        await db.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username)
        )
        await db.commit()

asyncio.run(reset_password("username", "newpassword"))
```

## 🐛 调试技巧

- **前端调试**：使用 Vue DevTools 浏览器扩展
- **后端调试**：查看终端输出的 FastAPI 日志
- **WebSocket 调试**：使用浏览器开发者工具的 Network > WS 标签
- **数据库调试**：使用 SQLite 客户端工具（如 DB Browser for SQLite）查看 `chatbox.db`
- **认证调试**：检查浏览器 localStorage 中的 tokens，使用 jwt.io 解码查看内容

## 🔒 安全建议

### 生产环境
1. **JWT 密钥**：使用强随机密钥，不要使用示例密钥
2. **HTTPS**：生产环境必须使用 HTTPS，保护 token 传输
3. **CORS**：限制允许的前端域名，不要使用 `*`
4. **密码策略**：考虑增加密码强度要求（大小写、数字、特殊字符）
5. **速率限制**：添加 API 速率限制，防止暴力破解
6. **文件上传**：限制文件大小和类型，防止恶意上传
7. **数据库备份**：定期备份数据库
8. **日志监控**：记录登录失败、异常访问等安全事件

### 开发环境
- 不要将 `.env` 文件提交到版本控制
- 使用 `.env.example` 作为模板
- 定期更新依赖包，修复安全漏洞

## 📝 待办事项

- [x] 用户认证系统（JWT）
- [x] 聊天历史记录加载
- [x] Token 自动刷新
- [x] 表情选择器扩展（300+ 表情）
- [ ] 消息已读/未读状态
- [ ] 支持消息撤回功能
- [ ] 添加聊天室成员列表
- [ ] 实现私聊功能
- [ ] 消息搜索功能
- [ ] 文件下载功能
- [ ] 多语言支持

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

---

**Happy Coding! 🎉**
