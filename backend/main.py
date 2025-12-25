from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import init_db, create_room, get_rooms, get_room, save_message, get_room_messages
from models import RegisterRequest, LoginRequest, TokenResponse, UserResponse, UpdateProfileRequest, RefreshTokenRequest, User, ChangePasswordRequest
from auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from crud import create_user, get_user_by_username, get_user_by_id, update_user, save_refresh_token, verify_refresh_token, delete_refresh_token, change_password
from dependencies import get_current_user, get_current_user_optional
from config import REFRESH_TOKEN_EXPIRE_DAYS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class RoomCreate(BaseModel):
    name: str
    password: Optional[str] = None

class RoomJoin(BaseModel):
    room_id: str
    password: Optional[str] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[tuple[WebSocket, str]]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append((websocket, username))

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id] = [
                (ws, user) for ws, user in self.active_connections[room_id] if ws != websocket
            ]

    def get_online_users(self, room_id: str) -> List[str]:
        if room_id in self.active_connections:
            return list(set([user for _, user in self.active_connections[room_id]]))
        return []

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for websocket, _ in self.active_connections[room_id]:
                await websocket.send_json(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/rooms")
async def create_new_room(room: RoomCreate):
    room_id = str(uuid.uuid4())[:8]
    await create_room(room_id, room.name, room.password)
    return {"id": room_id, "name": room.name}

@app.get("/api/rooms")
async def list_rooms():
    rooms = await get_rooms()
    # Add online user count to each room
    for room in rooms:
        room["online_count"] = len(manager.get_online_users(room["id"]))
    return rooms

@app.post("/api/rooms/join")
async def join_room(room_join: RoomJoin):
    room = await get_room(room_join.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["password"] and room["password"] != room_join.password:
        raise HTTPException(status_code=403, detail="Invalid password")
    return {"success": True, "room": room}

@app.get("/api/rooms/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 100):
    messages = await get_room_messages(room_id, limit)
    return messages

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", file_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/uploads/{file_name}"}

# Authentication endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    # Check if username already exists
    existing_user = await get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Validate password length
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Create user
    user = await create_user(request.username, request.password, request.display_name, request.email)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Generate tokens
    access_token = create_access_token({"user_id": user.id, "username": user.username})
    refresh_token = create_refresh_token({"user_id": user.id})

    # Save refresh token
    expires_at = (datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    await save_refresh_token(user.id, refresh_token, expires_at)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    # Get user
    user = await get_user_by_username(request.username)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate tokens
    access_token = create_access_token({"user_id": user.id, "username": user.username})
    refresh_token = create_refresh_token({"user_id": user.id})

    # Save refresh token
    expires_at = (datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    await save_refresh_token(user.id, refresh_token, expires_at)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest):
    # Verify refresh token
    user_id = await verify_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Get user
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Generate new tokens
    access_token = create_access_token({"user_id": user.id, "username": user.username})
    new_refresh_token = create_refresh_token({"user_id": user.id})

    # Delete old refresh token and save new one
    await delete_refresh_token(request.refresh_token)
    expires_at = (datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    await save_refresh_token(user.id, new_refresh_token, expires_at)

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)

@app.post("/api/auth/logout")
async def logout(request: RefreshTokenRequest, current_user: User = Depends(get_current_user)):
    await delete_refresh_token(request.refresh_token)
    return {"success": True}

# User profile endpoints
@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )

@app.put("/api/users/me", response_model=UserResponse)
async def update_current_user_profile(request: UpdateProfileRequest, current_user: User = Depends(get_current_user)):
    updated_user = await update_user(
        current_user.id,
        display_name=request.display_name,
        email=request.email,
        avatar_url=request.avatar_url
    )
    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        display_name=updated_user.display_name,
        email=updated_user.email,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at
    )

@app.post("/api/users/me/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"avatar_{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", file_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/uploads/{file_name}"
    await update_user(current_user.id, avatar_url=avatar_url)

    return {"avatar_url": avatar_url}

@app.post("/api/users/me/password")
async def change_user_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    # Verify old password
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少需要6个字符")

    # Change password
    new_password_hash = hash_password(request.new_password)
    await change_password(current_user.id, new_password_hash)

    return {"success": True, "message": "密码修改成功"}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: Optional[str] = None, token: Optional[str] = None):
    # Determine user identity
    display_username = username
    user_id = None
    is_guest = True

    if token:
        # Authenticated user
        payload = verify_token(token)
        if payload:
            user_id = payload.get("user_id")
            if user_id:
                user = await get_user_by_id(user_id)
                if user:
                    display_username = user.display_name or user.username
                    is_guest = False

    if not display_username:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room_id, display_username)

    # Send join notification
    join_message = {
        "type": "system",
        "action": "join",
        "username": display_username,
        "online_users": manager.get_online_users(room_id)
    }
    await manager.broadcast(join_message, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await save_message(room_id, data["username"], data["content"], data["type"], user_id, is_guest)
            await manager.broadcast(data, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

        # Send leave notification
        leave_message = {
            "type": "system",
            "action": "leave",
            "username": display_username,
            "online_users": manager.get_online_users(room_id)
        }
        await manager.broadcast(leave_message, room_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
