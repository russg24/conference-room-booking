import os
import jwt
import datetime
import bcrypt
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Helper function to get a database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database='postgres',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Auth Service"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Find the user in the database
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        # 2. Check if user exists AND password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            # 3. Create the Key (JWT Token)
            token = jwt.encode({
                'user_id': user[0],
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Expires in 1 hour
            }, os.getenv('JWT_SECRET'), algorithm='HS256')

            return jsonify({"token": token})
        
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5001 to avoid clashing with Weather Service (5000)
    app.run(host='0.0.0.0', port=5001)