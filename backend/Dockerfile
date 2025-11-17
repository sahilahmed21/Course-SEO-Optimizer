# Use an official, lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install dependencies
# Copy only the requirements file first to leverage Docker's cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 2. Copy your application code
# This copies your 'app' folder into the container's 'app' folder
COPY ./app ./app

# 3. Expose the port the app runs on
EXPOSE 8000

# 4. Define the command to run your app
# This runs uvicorn on 0.0.0.0 to make it accessible outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]