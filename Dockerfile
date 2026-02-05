# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src/api.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "src/api.py"]
