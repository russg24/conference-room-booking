import random
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Weather Service"}), 200

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    # Normalize city name to lowercase for easy matching
    city_name = city.lower()

    # --- CONTROLLED RANDOMNESS LOGIC ---
    if 'london' in city_name:
        # Always cold, but varies slightly (9°C to 14°C)
        temp = random.randint(9, 14)
        condition = "Rainy"
        
    elif 'berlin' in city_name:
        # Always mild (14°C to 19°C)
        temp = random.randint(14, 19)
        condition = "Cloudy"
        
    elif 'paris' in city_name:
        # Always warm (18°C to 25°C)
        temp = random.randint(18, 25)
        condition = "Sunny"
        
    else:
        # Default for unknown cities
        temp = 20
        condition = "Clear"

    # Return the Data
    return jsonify({
        "city": city.title(),
        "temperature": temp,
        "condition": condition,
        "timestamp": time.time()
    }), 200

if __name__ == '__main__':
    # Run on Port 5000 (Weather Service Port)
    app.run(host='0.0.0.0', port=5000)