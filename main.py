from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from security.security import check_user_ws, hash_password, check_password, create_access_token
from database.model import Users, ChatMessage
from database.database import get_db
from pydantic import BaseModel
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LiveLink Engine")

class UserCreate(BaseModel):
    name: str
    email : str
    password : str

class LoginUser(BaseModel):
    email : str
    password : str

rooms : dict[str, dict[str, WebSocket]] = {}

@app.post("/register", status_code=201)
def create_user(data : UserCreate ,db : Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    clean_name = data.name.strip()
    clean_password = data.password.strip()
    check_duplication = db.query(Users).filter(Users.email == clean_email).first()
    if check_duplication:
        raise HTTPException(status_code=401, detail=f"User with email {clean_email} already exists")
    hashed_password = hash_password(clean_password)
    new_user = Users(name=clean_name, email=clean_email, password = hashed_password)
    db.add(new_user)
    db.commit()
    return {"Message" : "User created successfully"}

@app.post("/login")
def login_user(data : LoginUser, db: Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    plain_pass = data.password.strip()
    check_user = db.query(Users).filter(Users.email == clean_email).first()
    if not check_user:
        raise HTTPException(status_code=404, detail=f"email or password is incorrect")
    if check_password(plain_pass, check_user.password):
        token = create_access_token(check_user.id, check_user.email)
        return {"token" : token, "type" : "bearer"}
    raise HTTPException(status_code=401, detail="email or password is incorrect")


@app.websocket("/ws/{room_name}")
async def user(websocket : WebSocket, room_name : str = "public", current_user : Users = Depends(check_user_ws), db : Session = Depends(get_db)):
    room_key = room_name.strip().lower()
    clean_username = current_user.email.strip().lower()
    await websocket.accept()
    if room_key not in rooms:
        rooms[room_key] = {}

    if clean_username in rooms[room_key]:
        await websocket.send_text(f"User with email {current_user.email} already exists")
        await websocket.close()
        return

    rooms[room_key][clean_username] = websocket
    print(f"{current_user.name} joined in the room. Total users : {len(rooms[room_key])}")
    for client_Socket in rooms[room_key].values():
        await client_Socket.send_text(f"{current_user.name} joined the chat")
    message_history = db.query(ChatMessage).filter(ChatMessage.room_name == room_key).order_by(ChatMessage.id.desc()).limit(100).all()
    for message in reversed(message_history):
        await websocket.send_text(f"{message.sender_name} : {message.content}")
    try:
        while True:
            data = await websocket.receive_text()
            new_msg = ChatMessage(
                room_name = room_key,
                sender_name = current_user.name,
                content = data
            )
            db.add(new_msg)
            db.commit()
            for client_Socket in rooms[room_key].values():
                await client_Socket.send_text(f"{current_user.name} : {data}")
    except WebSocketDisconnect:
        del rooms[room_key][clean_username]
        print("Client disconnected cleanly")