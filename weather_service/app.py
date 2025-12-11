from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- EXPLANATION: AWS CONNECTION ---
# We connect to DynamoDB using "boto3".
# We use 'os.getenv' to grab secrets from the environment so we don't hardcode passwords.
# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')  # <--- THIS WAS MISSING!
)
# This connects to the specific table you created in your design
table = dynamodb.Table('WeatherForecast')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- EXPLANATION: THE MAIN LOGIC ---
# This matches your UML diagram: GET /forecast?location_id=...&date=...
@app.route('/forecast', methods=['GET'])
def get_forecast():
    # 1. Get parameters from the URL
    location_id = request.args.get('location_id')
    date = request.args.get('date')

    if not location_id or not date:
        return jsonify({"error": "Please provide location_id and date"}), 400

    try:
        # 2. Try to find the data in DynamoDB
        response = table.get_item(Key={'location_id': location_id, 'date': date})
        
        if 'Item' in response:
            # Found it! Return the real data.
            # We convert Decimal to float because JSON doesn't like AWS Decimals.
            return jsonify({
                "location_id": location_id,
                "date": date,
                "temp_c": float(response['Item']['temp_c'])
            }), 200
        else:
            # 3. FALLBACK (Very important for dev)
            # If the DB is empty (which it is right now), return a dummy value
            # so the frontend doesn't crash.
            return jsonify({
                "message": "Forecast not found, returning simulation", 
                "temp_c": 21.0
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(host='0.0.0.0', port=5000)