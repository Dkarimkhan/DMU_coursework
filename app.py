from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

print("BACKEND STARTED")

# ПОДКЛЮЧЕНИЕ К MYSQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="college_database"
)

cursor = db.cursor()

# =========================
# CREATE TABLES AUTOMATICALLY
# =========================

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    user_type VARCHAR(50)
)
""")

# COURSES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100),
    course_description TEXT
)
""")

# MODULES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS modules (
    module_id INT AUTO_INCREMENT PRIMARY KEY,
    module_name VARCHAR(100),
    course_id INT,

    FOREIGN KEY (course_id)
    REFERENCES courses(course_id)
)
""")

# ENROLLMENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT,
    course_id INT,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id),

    FOREIGN KEY (course_id)
    REFERENCES courses(course_id)
)
""")

db.commit()

# =========================
# HOME
# =========================

@app.route('/')
def home():
    return "Backend connected successfully!"

# =========================
# REGISTER
# =========================

@app.route('/register', methods=['POST'])
def register():

    data = request.json

    name = data['name']
    email = data['email']
    password = data['password']

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    cursor.execute(
        """
        INSERT INTO users
        (name, email, password, user_type)

        VALUES (%s, %s, %s, %s)
        """,
        (name, email, password, "student")
    )

    db.commit()

    return jsonify({
        "message": "User registered successfully"
    })

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']
    password = data['password']

    cursor.execute(
        """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """,
        (email, password)
    )

    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful"
        })

    return jsonify({
        "message": "Invalid email or password"
    }), 401

# =========================
# RUN SERVER
# =========================

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 186c47f (Add Flask backend and MySQL database)
