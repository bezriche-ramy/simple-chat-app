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

@socketio.on('connect'):
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

if __name__ == '__main__':
    socketio.run(app)