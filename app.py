from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

print("BACKEND STARTED")

# =========================
# DATABASE CONNECTION
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="college_database"
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
        user_type VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id INT AUTO_INCREMENT PRIMARY KEY,
        course_name VARCHAR(100),
        course_description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        module_id INT AUTO_INCREMENT PRIMARY KEY,
        module_name VARCHAR(100),
        course_id INT,
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        course_id INT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
    """)

    db.commit()
    cursor.close()

init_db()

# =========================
# SEED COURSES (AUTO)
# =========================

def seed_courses():
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Seeding courses...")

        cursor.execute("""
        INSERT INTO courses (course_name, course_description)
        VALUES
        ('Intro to Programming', 'Python basics'),
        ('Web Development', 'HTML CSS JS'),
        ('Database Management', 'MySQL')
        """)

        db.commit()

        print("Courses added!")

    cursor.close()

seed_courses()

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

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email already exists"}), 400

        cursor.execute("""
            INSERT INTO users (name, email, password, user_type)
            VALUES (%s, %s, %s, %s)
        """, (name, email, password, "student"))

        db.commit()

        cursor.execute("""
            SELECT user_id, name, email, user_type
            FROM users
            WHERE email=%s
        """, (email,))

        user = cursor.fetchone()

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "user_type": user[3]
            }
        })

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"message": "Server error"}), 500

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data.get('email')
    password = data.get('password')

    cursor = db.cursor()

    cursor.execute("""
        SELECT user_id, name, email, user_type
        FROM users
        WHERE email=%s AND password=%s
    """, (email, password))

    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful",
            "user": {
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "user_type": user[3]
            }
        })

    return jsonify({"message": "Invalid email or password"}), 401

# =========================
# PROFILE
# =========================

@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):

    cursor = db.cursor()

    cursor.execute("""
        SELECT user_id, name, email, user_type
        FROM users
        WHERE user_id=%s
    """, (user_id,))

    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "user_type": user[3]
    })

# =========================
# COURSES
# =========================

@app.route('/courses', methods=['GET'])
def get_courses():

    cursor = db.cursor()
    cursor.execute("SELECT * FROM courses")

    rows = cursor.fetchall()

    courses = []

    for r in rows:
        courses.append({
            "course_id": r[0],
            "name": r[1],
            "description": r[2]
        })

    return jsonify(courses)

# =========================
# MODULES
# =========================

@app.route('/courses/<int:course_id>/modules', methods=['GET'])
def get_modules(course_id):

    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM modules
        WHERE course_id=%s
    """, (course_id,))

    rows = cursor.fetchall()

    modules = []

    for r in rows:
        modules.append({
            "module_id": r[0],
            "module_name": r[1],
            "course_id": r[2]
        })

    return jsonify(modules)

# =========================
# ENROLL (FIXED)
# =========================

@app.route('/enroll', methods=['POST'])
def enroll():

    data = request.json
    print("ENROLL DATA:", data)

    user_id = data.get('user_id')
    course_id = data.get('course_id')

    if not user_id or not course_id:
        return jsonify({"message": "Missing data"}), 400

    cursor = db.cursor()

    try:
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

    except Exception as e:
        print("ENROLL ERROR:", e)
        return jsonify({
            "message": "Server error",
            "error": str(e)
        }), 500

# =========================
# RUN SERVER
# =========================

if __name__ == '__main__':
    app.run(debug=True)