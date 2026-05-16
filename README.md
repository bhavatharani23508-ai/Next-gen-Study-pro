📚 Study Planner App
A Flask‑based web application designed to help students organize study sessions, manage tasks, and collaborate in secure rooms. The app allows users to create rooms with passwords, add tasks with deadlines, and view progress, making group study more structured and efficient.

🚀 Features
Room Management: Create and join study rooms with password protection.

Task Management: Add tasks with deadlines to specific rooms.

Deadline Tracking: Keep track of upcoming assignments and study goals.

Progress View: Display tasks in a structured format for each room.

Simple UI: Forms for room creation, joining, and task addition.

🛠️ Tech Stack
Backend: Flask (Python)

Frontend: HTML, CSS (templates)

Data Storage: In‑memory dictionary (can be extended to SQLite/MySQL)

Utilities: Webbrowser auto‑open, threading for startup

📂 Project Structure
Code
Study-Planner/
│── app.py              # Main Flask application
│── templates/
│   ├── index.html       # Home page (create/join room, add tasks)
│   ├── tasks.html       # Task view page
│── static/
│   └── style.css        # Styling
⚡ Getting Started
Clone the repository:

bash
git clone https://github.com/your-username/study-planner.git
cd study-planner
Create a virtual environment and install Flask:

bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install flask
Run the app:

bash
python app.py
Open in browser: http://127.0.0.1:5000

🎯 Future Enhancements
User authentication (Flask‑Login)

Database integration (SQLite/MySQL)

Calendar view for deadlines

Notifications/reminders for tasks

File sharing (notes, PDFs)

📖 License
This project is open‑source under the MIT License.
