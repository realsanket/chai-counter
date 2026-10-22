# The recipe for Chai Counter's container image: code + runtime + dependencies, packed together.

# 1. Start from an image that already has Python installed (the runtime)
FROM python:3.12-slim

# 2. Inside the image, work in the /app folder
WORKDIR /app

# 3. Install the dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the app's code
COPY . .

# 5. The app listens on port 8080 (set the same "target port" in Azure Container Apps)
EXPOSE 8080

# 6. Start the app with gunicorn, a production web server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
