# Base image
FROM python:3.12-slim
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Install system dependencies (important for PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
#Create app directory
WORKDIR /usr/src/app
#Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
#Copy the project file into the container
COPY . .
#Expose the Django app port
EXPOSE 8000
#Command to run the app 
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]


