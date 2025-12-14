import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database='postgres',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Room Service"}), 200

# 1. Get ALL Rooms (For the 'Three Boxes' selection screen)
@app.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Order by location so they are grouped nicely (Berlin, London, Paris)
        cur.execute('SELECT * FROM rooms ORDER BY location, price_per_hour;')
        rooms = cur.fetchall()
        cur.close()
        conn.close()

        rooms_list = []
        for r in rooms:
            rooms_list.append({
                "id": r[0],
                "name": r[1],
                "capacity": r[2],
                "location": r[3],
                "price_per_hour": float(r[4])
            })
        return jsonify(rooms_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Get Single Room (For the Dashboard & Booking Logic)
@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM rooms WHERE id = %s', (room_id,))
        r = cur.fetchone()
        cur.close()
        conn.close()

        if r:
            return jsonify({
                "id": r[0],
                "name": r[1],
                "capacity": r[2],
                "location": r[3],
                "price_per_hour": float(r[4])
            }), 200
        else:
            return jsonify({"error": "Room not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5002
    app.run(host='0.0.0.0', port=5002)