# 用户认证系统实现计划

## 概述
为聊天应用添加JWT认证系统，同时保留游客模式。登录用户可以保存用户名、查看聊天历史、创建私密房间、设置头像。

## 用户需求
- **认证方式**: JWT Token
- **注册信息**: 用户名（必需）、密码（必需）、显示名称（可选）、邮箱（可选）
- **游客模式**: 保留，未登录用户可继续使用随机用户名
- **登录用户权限**: 保存用户名、聊天历史、创建私密房间、头像设置

## 实现步骤

### Phase 1: 后端基础设施（核心）

#### 1.1 添加依赖
**文件**: `backend/requirements.txt`
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
```

#### 1.2 创建配置文件
**新建**: `backend/config.py`
- 从环境变量加载JWT密钥和配置
- 定义token过期时间（access: 15分钟，refresh: 7天）

**新建**: `backend/.env`
```
JWT_SECRET_KEY=<生成随机密钥>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### 1.3 创建认证工具
**新建**: `backend/auth.py`
- `create_access_token()` - 生成JWT access token
- `create_refresh_token()` - 生成JWT refresh token
- `verify_token()` - 验证token并解析payload
- `hash_password()` - 使用bcrypt哈希密码
- `verify_password()` - 验证密码

#### 1.4 创建数据模型
**新建**: `backend/models.py`
- Pydantic模型：RegisterRequest, LoginRequest, UserResponse, TokenResponse等

#### 1.5 更新数据库
**修改**: `backend/database.py`

添加新表：
```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    email TEXT,
    avatar_url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 刷新token表
CREATE TABLE refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

修改现有表（向后兼容）：
```sql
-- messages表添加user_id和is_guest字段
ALTER TABLE messages ADD COLUMN user_id INTEGER;
ALTER TABLE messages ADD COLUMN is_guest BOOLEAN DEFAULT 1;

-- rooms表添加owner_id和is_private字段
ALTER TABLE rooms ADD COLUMN owner_id INTEGER;
ALTER TABLE rooms ADD COLUMN is_private BOOLEAN DEFAULT 0;
```

#### 1.6 创建CRUD操作
**新建**: `backend/crud.py`
- `create_user()` - 创建新用户
- `get_user_by_username()` - 根据用户名查询
- `get_user_by_id()` - 根据ID查询
- `update_user()` - 更新用户信息
- `save_refresh_token()` - 保存refresh token
- `verify_refresh_token()` - 验证refresh token
- `delete_refresh_token()` - 删除refresh token

### Phase 2: 后端API（核心）

#### 2.1 创建依赖注入
**新建**: `backend/dependencies.py`
- `get_current_user()` - 从token获取当前用户（必需认证）
- `get_current_user_optional()` - 可选认证（支持游客）

#### 2.2 添加认证端点
**修改**: `backend/main.py`

新增端点：
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新token
- `POST /api/auth/logout` - 登出（删除refresh token）
- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新用户信息
- `POST /api/users/me/avatar` - 上传头像

#### 2.3 修改WebSocket端点
**修改**: `backend/main.py` 中的 `websocket_endpoint()`
- 支持两种连接方式：
  - 游客：`?username=xxx`
  - 登录用户：`?token=xxx`
- 从token解析user_id和display_name
- 在ConnectionManager中跟踪user_id

### Phase 3: 前端基础设施（核心）

#### 3.1 扩展用户状态管理
**修改**: `frontend/src/stores/user.js`

扩展state：
```javascript
state: {
  // 游客模式字段
  username: '',
  isGuest: true,

  // 认证用户字段
  userId: null,
  displayName: '',
  email: '',
  avatarUrl: '',
  accessToken: '',
  refreshToken: '',
  isAuthenticated: false
}
```

新增actions：
- `register()` - 注册
- `login()` - 登录
- `logout()` - 登出
- `refreshAccessToken()` - 刷新token
- `updateProfile()` - 更新资料
- `uploadAvatar()` - 上传头像
- `loadAuthState()` - 从localStorage加载认证状态

#### 3.2 创建API服务层
**新建**: `frontend/src/services/api.js`
- 封装所有API调用
- 自动添加Authorization header
- 自动处理401错误和token刷新
- 重试失败的请求

#### 3.3 更新应用入口
**修改**: `frontend/src/main.js`
- 在app启动时调用`userStore.loadAuthState()`

### Phase 4: 前端UI（核心）

#### 4.1 创建认证模态框
**新建**: `frontend/src/components/AuthModal.vue`
- 登录/注册标签切换
- 表单验证
- 错误提示
- "继续作为游客"选项

#### 4.2 创建用户资料组件
**新建**: `frontend/src/components/UserProfile.vue`
- 显示用户头像和名称
- 下拉菜单：查看资料、编辑资料、登出
- 点击头像打开菜单

#### 4.3 创建资料编辑模态框
**新建**: `frontend/src/components/ProfileEditModal.vue`
- 编辑显示名称
- 编辑邮箱
- 上传头像
- 保存按钮

#### 4.4 修改首页
**修改**: `frontend/src/views/Home.vue`
- 游客模式：显示"登录/注册"按钮
- 登录模式：显示用户头像和UserProfile组件
- 保留游客的用户名编辑功能

#### 4.5 修改聊天页面
**修改**: `frontend/src/views/Chat.vue`
- 修改WebSocket连接逻辑：
  - 游客：`?username=xxx`
  - 登录用户：`?token=xxx`
- 在消息旁显示用户头像
- 登录用户显示display_name，游客显示username

### Phase 5: 扩展功能（可选）

#### 5.1 聊天历史
- 为登录用户保存消息到数据库
- 添加API端点获取历史消息
- 在Chat.vue中加载历史消息

#### 5.2 私密房间
- 只允许登录用户创建带密码的房间
- 在rooms表中标记owner_id
- UI上区分私密房间图标

#### 5.3 头像功能
- 实现头像上传和存储
- 在消息列表中显示头像
- 在在线用户列表中显示头像

## 关键文件清单

### 后端新建文件
- `backend/config.py` - 配置管理
- `backend/auth.py` - JWT和密码工具
- `backend/models.py` - Pydantic模型
- `backend/crud.py` - 数据库操作
- `backend/dependencies.py` - FastAPI依赖
- `backend/.env` - 环境变量

### 后端修改文件
- `backend/requirements.txt` - 添加依赖
- `backend/database.py` - 添加新表和迁移
- `backend/main.py` - 添加认证端点，修改WebSocket

### 前端新建文件
- `frontend/src/services/api.js` - API服务层
- `frontend/src/components/AuthModal.vue` - 登录/注册
- `frontend/src/components/UserProfile.vue` - 用户资料
- `frontend/src/components/ProfileEditModal.vue` - 编辑资料

### 前端修改文件
- `frontend/src/stores/user.js` - 扩展认证状态
- `frontend/src/main.js` - 加载认证状态
- `frontend/src/views/Home.vue` - 添加登录UI
- `frontend/src/views/Chat.vue` - 修改WebSocket连接

## 向后兼容性
- 保留username query参数支持游客
- messages表的user_id可为空
- 使用is_guest标志区分消息类型
- 现有localStorage中的username继续有效

## 安全考虑
- 密码最小6字符
- JWT密钥存储在环境变量
- 使用bcrypt哈希密码
- Access token短期有效（15分钟）
- Refresh token长期有效（7天）
- 生产环境使用HTTPS
