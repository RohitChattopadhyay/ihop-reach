FROM mongo:4.0.9

# Copy script
COPY ./setup.sh /src/setup.sh
RUN chmod 777 /src/setup.sh

WORKDIR /src
# For installing unzip package
RUN apt-get update
# Install unzip
RUN apt-get install unzip
# Command to start the image
CMD /src/setup.sh
