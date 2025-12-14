FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Port 5002 (Room Service)
EXPOSE 5002

CMD ["python", "app.py"]