from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

print("BACKEND STARTED")

# подключение к MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="collegeprototype_database"
)

cursor = db.cursor()

# HOME
@app.route('/')
def home():
    return "Backend connected to MySQL!"

# REGISTER
@app.route('/register', methods=['POST'])
def register():

    data = request.json

    name = data['name']
    email = data['email']
    password = data['password']

    # проверка существует ли email
    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    # добавление пользователя
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )

    db.commit()

    return jsonify({
        "message": "User registered successfully"
    })

# LOGIN
@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']
    password = data['password']

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
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

if __name__ == '__main__':
    app.run(debug=True)
