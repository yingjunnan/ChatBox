from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import os
from typing import Dict, List, Optional
from database import init_db, create_room, get_rooms, get_room, save_message

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

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", file_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/uploads/{file_name}"}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await manager.connect(websocket, room_id, username)

    # Send join notification
    join_message = {
        "type": "system",
        "action": "join",
        "username": username,
        "online_users": manager.get_online_users(room_id)
    }
    await manager.broadcast(join_message, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await save_message(room_id, data["username"], data["content"], data["type"])
            await manager.broadcast(data, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

        # Send leave notification
        leave_message = {
            "type": "system",
            "action": "leave",
            "username": username,
            "online_users": manager.get_online_users(room_id)
        }
        await manager.broadcast(leave_message, room_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
