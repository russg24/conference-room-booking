import os
import requests
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# We use defaults so it works on Localhost, but can be changed for AWS later
ROOM_SERVICE_URL = os.getenv('ROOM_SERVICE_URL', 'http://localhost:5002')
WEATHER_SERVICE_URL = os.getenv('WEATHER_SERVICE_URL', 'http://localhost:5000')

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database='postgres',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Booking Service"}), 200

# --- THE MAIN ENDPOINT: CREATE A BOOKING ---
@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    user_id = data.get('user_id')
    room_id = data.get('room_id')
    date = data.get('date')

    if not all([user_id, room_id, date]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        # 1. ORCHESTRATION: Get Room Details
        # We ask Room Service: "How much is this room and where is it?"
        room_response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{room_id}")
        if room_response.status_code != 200:
            return jsonify({"error": "Room not found"}), 404
        room_data = room_response.json()
        
        location = room_data['location']
        base_price = room_data['price_per_hour']
        room_name = room_data['name']

        # 2. ORCHESTRATION: Get Weather Details
        # We ask Weather Service: "What is the temp in this city?"
        weather_response = requests.get(f"{WEATHER_SERVICE_URL}/weather/{location}")
        current_temp = 20 # Default fallback
        if weather_response.status_code == 200:
            current_temp = weather_response.json()['temperature']

        # 3. ALGORITHM: Calculate Surcharge (CORRECTED)
        # Target is 21°C. We apply a PERCENTAGE surcharge based on the difference.
        target_temp = 21
        temp_diff = abs(target_temp - current_temp)
        
        surcharge_percentage = 0.0

        # Logic 
        if temp_diff < 2:
            surcharge_percentage = 0.0
        elif 2 <= temp_diff < 5:
            surcharge_percentage = 0.10  # 10%
        elif 5 <= temp_diff < 10:
            surcharge_percentage = 0.20  # 20%
        elif 10 <= temp_diff < 20:
            surcharge_percentage = 0.30  # 30%
        else: # >= 20
            surcharge_percentage = 0.50  # 50%

        # Calculate the extra cost based on the Base Price
        surcharge = base_price * surcharge_percentage
        
        # Final Total
        total_price = base_price + surcharge
        # 4. DATABASE: Save the Booking
        conn = get_db_connection()
        cur = conn.cursor()
        
        # This will fail if the room is already booked on this date (Double Booking Protection)
        cur.execute(
            """
            INSERT INTO bookings (user_id, room_id, room_name, date, total_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (user_id, room_id, room_name, date, total_price)
        )
        
        booking_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # 5. RESULT: Return the receipt
        return jsonify({
            "message": "Booking confirmed!",
            "booking_id": booking_id,
            "room": room_name,
            "location": location,
            "weather_temp": current_temp,
            "base_price": base_price,
            "surcharge": surcharge,
            "total_price": total_price
        }), 201

    except psycopg2.errors.UniqueViolation:
        # This catches the specific "Double Booking" database error
        return jsonify({"error": "This room is already booked for that date."}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DASHBOARD ENDPOINT: GET USER BOOKINGS ---
@app.route('/bookings/user/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE user_id = %s ORDER BY date DESC", (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        bookings = []
        for row in rows:
            bookings.append({
                "id": row[0],
                "room_name": row[3],
                "date": row[4],
                "total_price": float(row[5]),
                "created_at": str(row[6])
            })
        return jsonify(bookings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on Port 5004
    app.run(host='0.0.0.0', port=5004)