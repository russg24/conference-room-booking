#!/bin/bash

# --- 1. DYNAMIC CONFIGURATION ---
CODESPACE_URL_BASE="https://${CODESPACE_NAME}"
echo "🔧 CONFIGURING ENVIRONMENT..."
echo "Detected Codespace: ${CODESPACE_NAME}"

# Define the full URLs for your microservices
WEATHER_URL="${CODESPACE_URL_BASE}-5000.app.github.dev"
ROOM_URL="${CODESPACE_URL_BASE}-5002.app.github.dev"
BOOKING_URL="${CODESPACE_URL_BASE}-5004.app.github.dev"

# --- 2. INJECT URLS INTO FRONTEND FILES ---
# We do this FIRST so the code is ready when it starts
echo "💉 Injecting API URLs into frontend code..."

sed -i "s|const API_URL = \".*\";|const API_URL = \"${BOOKING_URL}\";|g" frontend/app.js
sed -i "s|const API_BASE = \".*\";|const API_BASE = \"${BOOKING_URL}\";|g" frontend/dashboard.html
sed -i "s|const API_BASE = \".*\";|const API_BASE = \"${BOOKING_URL}\";|g" frontend/login.html
sed -i "s|const API_ROOMS = \".*\";|const API_ROOMS = \"${ROOM_URL}\";|g" frontend/rooms.html
# Also inject Weather URL if you use it in rooms.html
sed -i "s|const API_WEATHER = \".*\";|const API_WEATHER = \"${WEATHER_URL}\";|g" frontend/rooms.html

echo "✅ URLs Updated."

# --- 3. START SERVICES ---
echo "🚀 Launching Microservices..."

# Start Weather Service
python weather_service/app.py > weather.log 2>&1 &
PID_WEATHER=$!

# Start Room Service
python room_service/app.py > room.log 2>&1 &
PID_ROOM=$!

# Start Booking Service
python booking_service/app.py > booking.log 2>&1 &
PID_BOOKING=$!

# Start Frontend
cd frontend
python -m http.server 8000 > ../frontend.log 2>&1 &
PID_FRONT=$!
cd ..

echo "⏳ Waiting 5 seconds for services to boot..."
sleep 5

# --- 4. AUTOMATICALLY MAKE PORTS PUBLIC ---
# Now that services are running, we can unlock the ports
echo "🔓 Unlocking Ports (Public)..."
gh codespace ports visibility 5000:public -c $CODESPACE_NAME
gh codespace ports visibility 5002:public -c $CODESPACE_NAME
gh codespace ports visibility 5004:public -c $CODESPACE_NAME
gh codespace ports visibility 8000:public -c $CODESPACE_NAME
echo "✅ Ports are now Public."

echo "------------------------------------------------"
echo "✅ SYSTEM ONLINE"
echo "------------------------------------------------"
echo "🌍 Frontend: https://${CODESPACE_NAME}-8000.app.github.dev"
echo "------------------------------------------------"
echo "Press CTRL+C to stop all services."

# Wait for user to exit
trap "kill $PID_WEATHER $PID_ROOM $PID_BOOKING $PID_FRONT; exit" SIGINT
wait