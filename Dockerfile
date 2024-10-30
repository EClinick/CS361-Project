# Use the official Python slim image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports (adjust as needed)
EXPOSE 8501 5001 5002 5003 5004

# Default command (can be overridden in docker-compose.yml)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]