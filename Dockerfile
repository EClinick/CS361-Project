# Use the official Python slim image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all application files first
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for persistent data
RUN mkdir -p /app/data

# Move the initial filter preferences file to data directory
RUN mv /app/filter_preferences.json /app/data/

# Create a volume mount point
VOLUME /app/data

# Expose necessary ports
EXPOSE 8501 5001 5002 5003 5004

# Default command (can be overridden in docker-compose.yml)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]