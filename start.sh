#!/bin/bash

# --- 1. DETECT AWS PUBLIC IP ---
echo "🔧 CONFIGURING FOR AWS EC2..."
PUBLIC_IP=$(curl -s checkip.amazonaws.com)
echo "🌍 Detected Public IP: ${PUBLIC_IP}"

# Define the full URLs for your microservices
WEATHER_URL="http://${PUBLIC_IP}:5000"
ROOM_URL="http://${PUBLIC_IP}:5002"
BOOKING_URL="http://${PUBLIC_IP}:5004"

# --- 2. INJECT URLS INTO FRONTEND FILES ---
echo "💉 Injecting AWS IPs into frontend code..."
sed -i "s|const API_URL = \".*\";|const API_URL = \"${BOOKING_URL}\";|g" frontend/app.js
sed -i "s|const API_BASE = \".*\";|const API_BASE = \"${BOOKING_URL}\";|g" frontend/dashboard.html
sed -i "s|const API_BASE = \".*\";|const API_BASE = \"${BOOKING_URL}\";|g" frontend/login.html
sed -i "s|const API_ROOMS = \".*\";|const API_ROOMS = \"${ROOM_URL}\";|g" frontend/rooms.html
sed -i "s|const API_WEATHER = \".*\";|const API_WEATHER = \"${WEATHER_URL}\";|g" frontend/rooms.html
echo "✅ Frontend updated."

# --- 3. START SERVICES ---
echo "🚀 Launching Microservices..."
python weather_service/app.py > weather.log 2>&1 &
python room_service/app.py > room.log 2>&1 &
python booking_service/app.py > booking.log 2>&1 &

cd frontend
python -m http.server 8000 > ../frontend.log 2>&1 &
cd ..

echo "✅ SYSTEM ONLINE at http://${PUBLIC_IP}:8000"
# Keep script running
wait