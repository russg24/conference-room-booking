# 1. Use a lightweight version of Python (saves space)
FROM python:3.9-slim

# 2. Set the working folder inside the container
WORKDIR /app

# 3. Copy just the requirements first (caches dependencies)
COPY requirements.txt .

# 4. Install the libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. Tell the world this container listens on port 5000
EXPOSE 5000

# 7. The command to run when the container starts
CMD ["python", "app.py"]