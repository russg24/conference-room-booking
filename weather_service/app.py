import random
import time
import os
import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
def get_dynamo_table():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'), 
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    return dynamodb.Table('WeatherForecast')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Weather Service (AWS DynamoDB)"}), 200

@app.route('/weather', methods=['GET'])
def get_weather():
    # 1. Get Query Params
    city = request.args.get('location', 'Unknown')
    date_str = request.args.get('date', '2025-01-01') 
    city_id = city.lower()

    # --- 2. TRY TO READ FROM DYNAMODB ---
    try:
        table = get_dynamo_table()
        response = table.get_item(
            Key={
                'location_id': city_id,
                'date': date_str
            }
        )
        
        if 'Item' in response:
            # flush=True ensures this shows up instantly on your screen during the video!
            print(f"✅ FOUND in AWS DynamoDB: {city} on {date_str}", flush=True)
            item = response['Item']
            return jsonify({
                "location": item.get('display_name', city),
                "temperature": float(item['temperature']),
                "condition": item['condition'],
                "source": "AWS DynamoDB"
            }), 200
            
    except Exception as e:
        print(f"⚠️ DynamoDB Read Error (Using fallback): {str(e)}", flush=True)

    # --- 3. GENERATE IF NOT FOUND ---
    print(f"⚠️ NOT FOUND. Generating new data for {city}...", flush=True)

    if 'london' in city_id:
        temp, condition = random.randint(9, 14), "Rainy"
    elif 'berlin' in city_id:
        temp, condition = random.randint(14, 19), "Cloudy"
    elif 'paris' in city_id:
        temp, condition = random.randint(24, 29), "Sunny"
    else:
        temp, condition = 20, "Clear"

    # --- 4. WRITE TO DYNAMODB ---
    try:
        new_record = {
            'location_id': city_id,
            'date': date_str,
            'display_name': city.title(),
            'temperature': int(temp),
            'condition': condition,
            'created_at': str(time.time())
        }
        table.put_item(Item=new_record)
        print(f"✅ SAVED to AWS DynamoDB: {city_id}", flush=True)
    except Exception as e:
        print(f"❌ DynamoDB Write Error: {str(e)}", flush=True)

    return jsonify({
        "location": city.title(),
        "temperature": temp,
        "condition": condition,
        "source": "Generated (Saved to DB)"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)