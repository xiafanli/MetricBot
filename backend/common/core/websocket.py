from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"发送消息失败: {e}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"发送用户消息失败: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_alert(self, alert_data: dict):
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_alert_update(self, alert_id: int, status: str):
        message = {
            "type": "alert_update",
            "alert_id": alert_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)

    async def broadcast_stats_update(self, stats: dict):
        message = {
            "type": "stats_update",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)


manager = ConnectionManager()
