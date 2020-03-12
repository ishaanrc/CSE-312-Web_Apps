FROM ubuntu:18.04
RUN apt-get update
# Set the home directory to /root
ENV HOME /root
# cd into the home directory
WORKDIR /root
# Install Node
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev
# Copy all app files into the image
COPY . .
# Download dependancies
RUN pip install -r requirements.txt
# Allow port 8000 to be accessed
# from outside the container

EXPOSE 8000
ENV FLASK_APP=__init__.py
ENV FLASK_DEBUG=0
# Run the app
CMD flask run --port=8000