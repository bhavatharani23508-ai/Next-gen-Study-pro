from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import sqlite3
import webbrowser
from threading import Timer
import os
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "study-secret"

socketio = SocketIO(app, async_mode="threading")

users_online = 0

leaderboard = {}
room_users = {}
streaks = {}
camera_status = {}

# socket user tracking
user_rooms = {}

def init_db():

    conn = sqlite3.connect("study.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS rooms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT UNIQUE,
        password TEXT,
        room_type TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():

    conn = sqlite3.connect("study.db")
    c = conn.cursor()

    active_rooms = tuple(room_users.keys())

    if active_rooms:

        placeholders = ",".join("?" * len(active_rooms))

        c.execute(f"""
        SELECT room_name, room_type
        FROM rooms
        WHERE room_name IN ({placeholders})
        ORDER BY id DESC
        """, active_rooms)

        rooms = c.fetchall()

    else:
        rooms = []

    conn.close()

    return render_template(
        "index.html",
        rooms=rooms
    )

@app.route("/refresh_rooms")
def refresh_rooms():
    return redirect("/")

@app.route("/create_room", methods=["POST"])
def create_room():

    room_name = request.form["room_name"]
    password = request.form.get("password", "")
    room_type = request.form.get("room_type", "public")

    conn = sqlite3.connect("study.db")
    c = conn.cursor()

    try:

        c.execute("""
        INSERT INTO rooms(room_name,password,room_type)
        VALUES(?,?,?)
        """, (room_name, password, room_type))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return "Room already exists ❌"

    conn.close()

    session["username"] = request.form.get(
        "username",
        "Guest"
    )

    return render_template(
        "room.html",
        room_name=room_name
    )

@app.route("/join_room", methods=["POST"])
def join_room_route():

    room_name = request.form["room_name"]
    password = request.form.get("password", "")

    conn = sqlite3.connect("study.db")
    c = conn.cursor()

    c.execute("""
    SELECT room_name,password,room_type
    FROM rooms
    WHERE room_name=?
    """, (room_name,))

    room = c.fetchone()

    conn.close()

    if not room:
        return "Room not found ❌"

    _, db_password, room_type = room

    if room_type == "private" and password != db_password:
        return "Wrong password ❌"

    session["username"] = request.form.get(
        "username",
        "Guest"
    )

    return render_template(
        "room.html",
        room_name=room_name
    )

@socketio.on("connect")
def handle_connect():

    global users_online

    users_online += 1

    emit(
        "user_count",
        users_online,
        broadcast=True
    )
    emit(
        "leaderboard_update",
        sorted(
            leaderboard.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

@socketio.on("disconnect")
def handle_disconnect():

    global users_online

    if users_online > 0:
        users_online -= 1

    emit(
        "user_count",
        users_online,
        broadcast=True
    )

    sid = request.sid

    if sid in user_rooms:

        room = user_rooms[sid]["room"]
        username = user_rooms[sid]["username"]

        if room in room_users:

            if username in room_users[room]:
                room_users[room].remove(username)

            emit(
                "room_users",
                room_users.get(room, []),
                room=room
            )
            if len(room_users[room]) == 0:

                del room_users[room]

                conn = sqlite3.connect("study.db")
                c = conn.cursor()

                c.execute(
                    "DELETE FROM rooms WHERE room_name=?",
                    (room,)
                )

                conn.commit()
                conn.close()

        del user_rooms[sid]

@socketio.on("join")
def handle_join(data):

    room = data["room"]
    username = data.get("username", "Guest")

    join_room(room)

    user_rooms[request.sid] = {
        "room": room,
        "username": username
    }

    if room not in room_users:
        room_users[room] = []

    if username not in room_users[room]:
        room_users[room].append(username)

    emit(
        "message",
        f"👋 {username} joined the room",
        to=room
    )

    emit(
        "room_users",
        room_users[room],
        to=room
    )

@socketio.on("leave")
def handle_leave(data):

    room = data["room"]
    username = data.get("username", "Guest")

    leave_room(room)

    if room in room_users:

        if username in room_users[room]:
            room_users[room].remove(username)

        emit(
            "room_users",
            room_users.get(room, []),
            to=room
        )

        emit(
            "message",
            f"👋 {username} left the room",
            to=room
        )

        # delete room if empty
        if len(room_users[room]) == 0:

            del room_users[room]

            conn = sqlite3.connect("study.db")
            c = conn.cursor()

            c.execute(
                "DELETE FROM rooms WHERE room_name=?",
                (room,)
            )

            conn.commit()
            conn.close()


@socketio.on("message")
def handle_message(data):

    room = data["room"]
    msg = data["msg"]
    username = data.get("username", "Guest")

    send(msg, to=room)

    leaderboard[username] = leaderboard.get(username, 0) + 5

    emit(
        "leaderboard_update",
        sorted(
            leaderboard.items(),
            key=lambda x: x[1],
            reverse=True
        ),
        broadcast=True
    )

@socketio.on("typing")
def handle_typing(data):

    emit(
        "typing",
        {
            "username": data.get("username", "Someone"),
            "typing": True
        },
        room=data["room"],
        include_self=False
    )

@socketio.on("start_timer")
def start_timer(data):

    emit(
        "timer_started",
        {
            "minutes": data["minutes"],
            "started_at": datetime.now().isoformat()
        },
        room=data["room"]
    )

@socketio.on("study_done")
def study_done(data):

    username = data.get("username", "Guest")

    today = str(datetime.now().date())

    # streak
    if username not in streaks:

        streaks[username] = {
            "last_date": today,
            "count": 1
        }

    else:

        if streaks[username]["last_date"] != today:
            streaks[username]["count"] += 1

        streaks[username]["last_date"] = today

    leaderboard[username] = leaderboard.get(username, 0) + 10

    emit(
        "streak_update",
        streaks[username],
        broadcast=True
    )

    emit(
        "leaderboard_update",
        sorted(
            leaderboard.items(),
            key=lambda x: x[1],
            reverse=True
        ),
        broadcast=True
    )

@socketio.on("update_xp")
def update_xp(data):

    username = data["username"]
    xp = data["xp"]

    leaderboard[username] = xp

    emit(
        "leaderboard_update",
        sorted(
            leaderboard.items(),
            key=lambda x: x[1],
            reverse=True
        ),
        broadcast=True
    )

@socketio.on("camera_toggle")
def camera_toggle(data):

    room = data["room"]

    camera_status[data.get("username")] = data.get("camera")

    emit(
        "camera_status",
        data,
        room=room,
        include_self=False
    )
@socketio.on("webrtc_offer")
def webrtc_offer(data):

    emit(
        "webrtc_offer",
        data,
        room=data["room"],
        include_self=False
    )

@socketio.on("webrtc_answer")
def webrtc_answer(data):

    emit(
        "webrtc_answer",
        data,
        room=data["room"],
        include_self=False
    )

@socketio.on("webrtc_ice_candidate")
def webrtc_ice_candidate(data):

    emit(
        "webrtc_ice_candidate",
        data,
        room=data["room"],
        include_self=False
    )
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5001/")

if __name__ == "__main__":

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5001,
        debug=True
    )
