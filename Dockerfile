# Use an official CUDA runtime as a parent image
FROM nvidia/cuda:11.4.2-base-ubuntu20.04

# Set the working directory in the container

# Update the package list and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Git (if not already installed)
RUN apt-get update && apt-get install -y git
# Install Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app/

# Set environment variable for Python
ENV PYTHONPATH=/app

# Command to run on container start
CMD ["python3", "your_script.py"]

# Use Ubuntu 20.04 as the base image
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Git (if not already installed)
RUN apt-get update && apt-get install -y git

# Install Opencv Python
RUN pip install opencv-python

# Install numpy using pip
RUN pip install pandas

# Install PyTorch and torchvision
RUN pip install torch torchvision torchaudio

WORKDIR /Projects

RUN git clone -b main https://github.com/rikhsitlladeveloper/Advertisement_tracking.git

WORKDIR /Projects/Advertisement_tracking

# Set the entry point command to run your Python script (replace "your_script.py" with your script's name)
# CMD ["python3", "Sevimli_tv_Artel_reklama_detection.py"]