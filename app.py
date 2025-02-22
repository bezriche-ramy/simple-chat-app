from flask import Flask,render_template,request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# python store connect yser. key is socket id and value is username
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handel_connect():
    username = f"User{random.randint(1000,9999)}"
    
    gender = random.choice(["girl","boy"])
    
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"
    
    users[request.sid] = {"username":username,"avatar_url":avatar_url}
    
    emit('user_joined',{"username":username,"avatar_url":avatar_url},broadcast=True)

    emit("set_username",{"username":username})

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in users:
        user=users.pop(request.sid,None)
        if user:
            emit("user_left",{"username":user["username"]},broadcast=True)

@socketio.on("send_message")
def handle_send_message(data):
    user = users.get(request.sid)
    if user:
        emit("message",{"username":user["username"],"avatar_url":user["avatar_url"],"message":data["message"]},broadcast=True)

@socketio.on("typing")
def handle_typing():
    user = users.get(request.sid)
    if user:
        emit("typing",{"username":user["username"]},broadcast=True)

@socketio.on("update_username") 
def handle_update_username(data):
    user = users.get(request.sid)
    if user:
        old_username = user["username"]
        user["username"] = data["username"]
        # Emit to the user who changed their name
        emit("set_username", {"username": data["username"]})
        # Broadcast to all users about the name change
        emit("username_changed", {
            "old_username": old_username,
            "new_username": data["username"],
            "avatar_url": user["avatar_url"]
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)