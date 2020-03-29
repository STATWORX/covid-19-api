# Use the official image as a parent image
FROM python:3.7

# Copy the file from your host to your current location
COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt

# Set the working directory
WORKDIR /app

# Run the command inside your image filesystem
RUN pip install -r requirements.txt

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 80

# Run the specified command within the container.
CMD ["python", "main.py"]
