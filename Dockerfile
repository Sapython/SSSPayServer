# Python image to use.
FROM python:3.7.2-slim

ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
# ENTRYPOINT ["python", "app.py"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
