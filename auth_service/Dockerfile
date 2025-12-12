# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (to cache dependencies)
COPY requirements.txt .

# Install the Python tools
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Open port 5001 (matches your app.py)
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]