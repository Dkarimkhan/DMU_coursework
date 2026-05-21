from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

print("BACKEND STARTED")

# =========================
# DATABASE
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="itacademy_database"
)

# =========================
# INIT TABLES
# =========================

def init_db():
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        user_type VARCHAR(20) DEFAULT 'student'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id INT AUTO_INCREMENT PRIMARY KEY,
        course_name VARCHAR(150),
        course_description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        module_id INT AUTO_INCREMENT PRIMARY KEY,
        module_name VARCHAR(150),
        course_id INT,
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        course_id INT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
    )
    """)

    db.commit()
    cursor.close()

init_db()

# =========================
# SEED DATA (AUTO RESET SAFE)
# =========================

def seed_data():
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]

    if count == 0:

        cursor.execute("""
        INSERT INTO courses (course_name, course_description)
        VALUES
        ('Introduction to Programming', 'Learn Python basics'),
        ('Web Development', 'HTML CSS JS'),
        ('Database Systems', 'MySQL and databases'),
        ('Cybersecurity Fundamentals', 'Security, threats, encryption'),
        ('Data Science and Machine Learning', 'Data analysis + ML'),
        ('Network and Systems Administration', 'Networking + servers')
        """)

        db.commit()

        cursor.execute("""
        INSERT INTO modules (module_name, course_id)
        VALUES
        ('Python Basics', 1),
        ('Loops and Functions', 1),

        ('HTML & CSS', 2),
        ('JavaScript Basics', 2),

        ('SQL Queries', 3),
        ('Database Design', 3),

        ('Cybersecurity Intro', 4),
        ('Encryption Basics', 4),

        ('Data Analysis with Python', 5),
        ('Machine Learning Basics', 5),

        ('Networking Fundamentals', 6),
        ('Cloud Computing Basics', 6)
        """)

        db.commit()

    cursor.close()

seed_data()

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "Backend running successfully!"

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    name = data["name"]
    email = data["email"]
    password = data["password"]

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        return jsonify({"message": "Email already exists"}), 400

    cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
    """, (name, email, password))

    db.commit()

    return jsonify({"message": "User created successfully"})

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]

    cursor = db.cursor()

    cursor.execute("""
        SELECT user_id, name, email
        FROM users
        WHERE email=%s AND password=%s
    """, (email, password))

    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Invalid login"}), 401

    return jsonify({
        "user": {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }
    })

# =========================
# GET ALL COURSES (IMPORTANT FOR FRONTEND)
# =========================

@app.route("/courses", methods=["GET"])
def get_courses():
    cursor = db.cursor()

    cursor.execute("SELECT * FROM courses ORDER BY course_id")
    rows = cursor.fetchall()

    return jsonify([
        {
            "course_id": r[0],
            "name": r[1],
            "description": r[2]
        }
        for r in rows
    ])

# =========================
# GET SINGLE COURSE (FOR COURSE PAGE)
# =========================

@app.route("/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    cursor = db.cursor()

    cursor.execute("""
        SELECT course_id, course_name, course_description
        FROM courses
        WHERE course_id=%s
    """, (course_id,))

    c = cursor.fetchone()

    if not c:
        return jsonify({"message": "Course not found"}), 404

    cursor.execute("""
        SELECT module_name
        FROM modules
        WHERE course_id=%s
    """, (course_id,))

    modules = cursor.fetchall()

    return jsonify({
        "course_id": c[0],
        "name": c[1],
        "description": c[2],
        "modules": [m[0] for m in modules]
    })

# =========================
# ENROLL
# =========================

@app.route("/enroll", methods=["POST"])
def enroll():
    data = request.json

    user_id = data["user_id"]
    course_id = data["course_id"]

    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM enrollments
        WHERE user_id=%s AND course_id=%s
    """, (user_id, course_id))

    if cursor.fetchone():
        return jsonify({"message": "Already enrolled"}), 400

    cursor.execute("""
        INSERT INTO enrollments (user_id, course_id)
        VALUES (%s, %s)
    """, (user_id, course_id))

    db.commit()

    return jsonify({"message": "Enrolled successfully"})

# =========================
# PROFILE (USER COURSES)
# =========================

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    cursor = db.cursor()

    cursor.execute("""
        SELECT c.course_id, c.course_name
        FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        WHERE e.user_id=%s
    """, (user_id,))

    rows = cursor.fetchall()

    return jsonify([
        {
            "course_id": r[0],
            "course_name": r[1]
        }
        for r in rows
    ])

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)