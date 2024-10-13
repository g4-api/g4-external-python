# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Expose the port specified in config.toml (defaulting to 5000)
EXPOSE 5000 9999

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py

# Command to run the Flask application
CMD ["python", "app.py"]
