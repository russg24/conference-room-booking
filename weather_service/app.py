import random
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Weather Service"}), 200

# CHANGED: Route is just '/weather' to accept query params (?location=...)
@app.route('/weather', methods=['GET'])
def get_weather():
    # 1. Get the city from the Query Parameter 'location'
    # The Booking Service sends: /weather?location=London
    city = request.args.get('location', 'Unknown')
    
    # Normalize for matching
    city_name = city.lower()

    # --- CONTROLLED RANDOMNESS LOGIC ---
    if 'london' in city_name:
        # Always cold (9°C to 14°C) -> NO Surcharge
        temp = random.randint(9, 14)
        condition = "Rainy"
        
    elif 'berlin' in city_name:
        # Always mild (14°C to 19°C) -> 10% Surcharge sometimes
        temp = random.randint(14, 19)
        condition = "Cloudy"
        
    elif 'paris' in city_name:
        # Always warm (24°C to 29°C) -> Guaranteed High Surcharge
        # I bumped this up so you can easily test the 'High Temp' surcharge!
        temp = random.randint(24, 29)
        condition = "Sunny"
        
    else:
        # Default for unknown cities
        temp = 20
        condition = "Clear"

    # Return the Data
    return jsonify({
        "location": city.title(), # Booking Service looks for 'location'
        "temperature": temp,
        "condition": condition,
        "timestamp": time.time()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)