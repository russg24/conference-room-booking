import boto3
import os
from dotenv import load_dotenv

load_dotenv()

try:
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    table = dynamodb.Table('WeatherForecast')
    table.put_item(Item={'location_id': 'verify-now', 'date': '2025-12-21', 'temp': 20})
    print("✅ CONNECTION LIVE: Check AWS Console now!")
except Exception as e:
    print(f"❌ CONNECTION EXPIRED: {e}")