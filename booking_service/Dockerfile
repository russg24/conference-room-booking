FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Port 5004 (Booking Service)
EXPOSE 5004

CMD ["python", "app.py"]