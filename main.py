from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="LiveLink Engine")

rooms : dict[str, dict[str, WebSocket]] = {}

@app.websocket("/ws/{room_name}/{user_name}")
async def user(websocket : WebSocket, user_name : str, room_name : str = "public"):
    room_key = room_name.strip().lower()
    clean_username = user_name.strip().lower()
    await websocket.accept()
    if room_key not in rooms:
        rooms[room_key] = {}

    if clean_username in rooms[room_key]:
        await websocket.send_text(f"User with username {clean_username} already exists")
        await websocket.close()
        return

    rooms[room_key][clean_username] = websocket
    print(f"{clean_username} joined in the room. Total users : {len(rooms[room_key])}")
    for client_Socket in rooms[room_key].values():
        await client_Socket.send_text(f"{clean_username} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            for client_Socket in rooms[room_key].values():
                await client_Socket.send_text(f"{clean_username} : {data}")
    except WebSocketDisconnect:
        print("Client disconnected cleanly")