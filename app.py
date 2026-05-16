from flask import Flask, render_template, request
import webbrowser
from threading import Timer

app = Flask(__name__)
rooms = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create_room", methods=["POST"])
def create_room():
    room_name = request.form["room_name"]
    password = request.form["password"]
    rooms[room_name] = password
    return f"Room '{room_name}' created successfully 🎉"

@app.route("/join_room", methods=["POST"])
def join_room():
    room_name = request.form["room_name"]
    password = request.form["password"]
    if room_name in rooms and rooms[room_name] == password:
        return f"Welcome to {room_name} 🚀"
    return "Wrong password or room not found ❌"

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

import os

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()
    app.run(debug=True)
