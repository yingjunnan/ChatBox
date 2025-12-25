# 聊天室应用

一个基于 Vue 3 和 FastAPI 的实时聊天应用。

## 功能特性

- 随机生成用户名
- 创建聊天室（支持密码保护）
- 查看聊天室列表
- 直接输入房间ID加入
- 实时消息传输（WebSocket）
- 支持发送文字、表情、图片和视频

## 技术栈

### 前端
- Vue 3
- Vite
- Tailwind CSS
- Pinia (状态管理)
- Vue Router

### 后端
- FastAPI
- WebSockets
- SQLite (数据库)
- aiosqlite

## 安装和运行

### 后端

1. 进入后端目录:
```bash
cd backend
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 运行服务器:
```bash
python main.py
```

后端服务将在 http://localhost:8000 运行

### 前端

1. 进入前端目录:
```bash
cd frontend
```

2. 安装依赖:
```bash
npm install
```

3. 运行开发服务器:
```bash
npm run dev
```

前端应用将在 http://localhost:5173 运行

## 使用说明

1. 打开浏览器访问前端地址
2. 系统会自动生成一个随机用户名
3. 可以选择:
   - 创建新聊天室（可选设置密码）
   - 从列表中选择已有聊天室加入
   - 直接输入房间ID加入
4. 在聊天室中可以:
   - 发送文字消息
   - 点击表情按钮选择表情
   - 点击附件按钮上传图片或视频

## 项目结构

```
chatbox/
├── backend/
│   ├── main.py           # FastAPI 主应用
│   ├── database.py       # 数据库操作
│   ├── requirements.txt  # Python 依赖
│   └── uploads/          # 上传文件存储目录
└── frontend/
    ├── src/
    │   ├── views/        # 页面组件
    │   ├── stores/       # Pinia 状态管理
    │   ├── router/       # Vue Router 配置
    │   ├── App.vue       # 根组件
    │   └── main.js       # 入口文件
    └── package.json      # npm 依赖
```
