from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Add this line for session support
socketio = SocketIO(app)

# Store for users and messages
users = {}
message_history = []  # Store recent messages
MAX_MESSAGES = 50  # Maximum number of messages to store

@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/join', methods=['POST'])
def join():
    username = request.form.get('username', '').strip()
    gender = request.form.get('gender', 'boy')
    
    if len(username) < 3 or len(username) > 15:
        return redirect(url_for('login'))
    
    session['username'] = username
    session['gender'] = gender
    session['avatar_url'] = f"https://avatar.iran.liara.run/public/{gender}?username={username}"
    
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    if 'username' not in session:
        return False
    
    username = session['username']
    avatar_url = session['avatar_url']
    
    users[request.sid] = {
        "username": username,
        "avatar_url": avatar_url
    }
    
    # Send existing users to the new user
    existing_users = [{"username": user["username"], "avatar_url": user["avatar_url"]} 
                     for user in users.values()]
    emit('initialize_users', existing_users)
    
    # Send message history to the new user
    emit('message_history', message_history)
    
    # Broadcast new user to everyone
    emit('user_joined', {"username": username, "avatar_url": avatar_url}, broadcast=True)
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
        message_data = {
            "username": user["username"],
            "avatar_url": user["avatar_url"],
            "message": data["message"]
        }
        # Store message in history
        message_history.append(message_data)
        # Keep only recent messages
        if len(message_history) > MAX_MESSAGES:
            message_history.pop(0)
        emit("message", message_data, broadcast=True)

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

@socketio.on("clear_history")
def handle_clear_history():
    global message_history
    message_history = []
    emit("history_cleared", broadcast=True)

if __name__ == '__main__':
    socketio.run(app)