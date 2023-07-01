# Use the Python3.7.2 image
# FROM ubuntu:20.04
FROM python:3.8-slim-buster
# FROM python:3-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
COPY ./requirements.txt /app/requirements.txt

COPY . /app


# Install the dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx
# RUN apt-get install -y libgtk2.0-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN pip install opencv-python
RUN pip install opencv-python-headless
RUN pip install python-dotenv
RUN pip install waitress
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
# CMD ["python3", "app.py"]