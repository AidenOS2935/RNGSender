# Use an official Python runtime as a parent image
FROM --platform=$BUILDPLATFORM python:3.9-slim AS build

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 3645 available to the world outside this container
EXPOSE 3645

# Define environment variable
ENV FLASK_APP=index.py

# Run Gunicorn when the container launches
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:3645", "index:app"]
