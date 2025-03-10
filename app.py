from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import bcrypt
import jwt
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('schools.db')
    conn.row_factory = sqlite3.Row
    return conn

# 建立資料庫與表格
with get_db_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS school_cutoffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cutoff_score INTEGER NOT NULL
        )
    ''')
    conn.commit()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/schools', methods=['GET'])
def get_schools():
    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM school_cutoffs').fetchall()
    conn.close()
    return jsonify([dict(school) for school in schools])

@app.route('/schools', methods=['POST'])
def add_school():
    data = request.json
    name = data.get('name')
    cutoff_score = data.get('cutoff_score')

    if not name or cutoff_score is None:
        return jsonify({'error': 'Missing name or cutoff_score'}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO school_cutoffs (name, cutoff_score) VALUES (?, ?)', (name, cutoff_score))
    conn.commit()
    conn.close()

    return jsonify({'message': 'School added successfully'}), 201

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    scores = data.get('scores')

    conn = get_db_connection()
    schools = conn.execute('SELECT * FROM school_cutoffs').fetchall()
    conn.close()

    result = {'safe_schools': [], 'target_schools': [], 'challenge_schools': []}
    total_score = sum(scores.values())

    for school in schools:
        cutoff = school['cutoff_score']
        if total_score >= cutoff + 3:
            result['safe_schools'].append(school['name'])
        elif total_score >= cutoff:
            result['target_schools'].append(school['name'])
        else:
            result['challenge_schools'].append(school['name'])

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
