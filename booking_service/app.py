import os
import requests
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, date  # Critical import for date checking

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
ROOM_SERVICE_URL = os.getenv('ROOM_SERVICE_URL', 'http://localhost:5002')
WEATHER_SERVICE_URL = os.getenv('WEATHER_SERVICE_URL', 'http://localhost:5000')

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASS', 'postgres')
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
    room_name = data.get('room_name')
    date_str = data.get('date') # Use date_str to be clear it's a string first
    
    # NEW: Check if this is just a preview (Quote)
    is_preview = data.get('preview', False)

    if not all([user_id, room_id, date_str]):
        return jsonify({"error": "Missing fields"}), 400

    # --- NEW: BLOCK PAST DATES ---
    try:
        # Convert string "2025-10-24" to a Python Date Object
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = date.today()

        if booking_date < today:
            return jsonify({
                "error": f"Cannot book in the past. Today is {today}, you asked for {booking_date}"
            }), 400
            
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    # -----------------------------

    try:
        # 1. ORCHESTRATION: Get Room Details
        room_response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{room_id}")
        if room_response.status_code != 200:
            return jsonify({"error": "Room not found"}), 404
        room_data = room_response.json()
        
        location = room_data.get('location', 'Unknown')
        base_price = room_data.get('price_per_hour') or room_data.get('base_price', 0)
        
        # 2. ORCHESTRATION: Get Weather Details
        current_temp = 20 
        try:
            weather_response = requests.get(f"{WEATHER_SERVICE_URL}/weather?location={location}&date={date_str}")
            if weather_response.status_code == 200:
                current_temp = weather_response.json().get('temperature', 20)
        except:
            print("Weather service unavailable, using default.")

        # 3. ALGORITHM: Calculate Surcharge
        target_temp = 21
        temp_diff = abs(target_temp - current_temp)
        surcharge_percentage = 0.0

        if temp_diff < 2:
            surcharge_percentage = 0.0
        elif 2 <= temp_diff < 5:
            surcharge_percentage = 0.10  # 10%
        elif 5 <= temp_diff < 10:
            surcharge_percentage = 0.20  # 20%
        elif 10 <= temp_diff < 20:
            surcharge_percentage = 0.30  # 30%
        else: 
            surcharge_percentage = 0.50  # 50%

        surcharge = base_price * surcharge_percentage
        total_price = base_price + surcharge

        # --- PREVIEW MODE ---
        if is_preview:
            return jsonify({
                "message": "Price Preview Calculated",
                "room": room_name,
                "date": date_str,
                "location": location,
                "weather_temp": current_temp,
                "base_price": base_price,
                "surcharge": surcharge,
                "total_price": total_price,
                "status": "PREVIEW_ONLY"
            }), 200

        # 4. DATABASE: Save the Booking (Only if NOT preview)
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check for existing booking manually (Double Booking Protection)
        cur.execute("SELECT id FROM bookings WHERE room_id = %s AND date = %s", (room_id, date_str))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Room already booked for this date"}), 409

        cur.execute(
            """
            INSERT INTO bookings (user_id, room_id, room_name, date, total_price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (user_id, room_id, room_name, date_str, total_price)
        )
        
        booking_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # 5. RESULT: Return the receipt
        return jsonify({
            "message": "Booking confirmed!",
            "id": booking_id,
            "room": room_name,
            "location": location,
            "weather_temp": current_temp,
            "base_price": base_price,
            "surcharge": surcharge,
            "total_price": total_price
        }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Room already booked for this date"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DASHBOARD ENDPOINT ---
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
                "created_at": str(row[6]) if len(row) > 6 else ""
            })
        return jsonify(bookings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NEW: DELETE BOOKING ENDPOINT ---
@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if booking exists first
        cur.execute("SELECT id FROM bookings WHERE id = %s", (booking_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Booking not found"}), 404

        # Delete it
        cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Booking deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)