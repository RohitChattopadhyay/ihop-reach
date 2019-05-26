FROM mongo:4.0.9

# Copy script
COPY ./setup.sh /home/setup.sh
RUN chmod 777 /home/setup.sh

WORKDIR /home
# For installing unzip package
RUN apt-get update
# Install wget and unzip 
RUN apt-get install wget
RUN apt-get install unzip
# Command to start the image
CMD /home/setup.sh
