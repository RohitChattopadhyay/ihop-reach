#!/bin/bash

# Initialize a mongo data folder and logfile
mkdir -p /data/db
touch /var/log/mongodb.log
chmod 777 /var/log/mongodb.log
echo "Starting MongoDB"
# Start mongodb with logging
# --logpath    Without this mongod will output all log information to the standard output.
# --logappend  Ensure mongod appends new entries to the end of the logfile. We create it first so that the below tail always finds something
docker-entrypoint.sh mongod --logpath /var/log/mongodb.log --logappend &

# Wait until mongo logs that it's ready (or timeout after 60s)
COUNTER=0
grep -q 'waiting for connections on port' /var/log/mongodb.log
while [[ $? -ne 0 && $COUNTER -lt 60 ]] ; do
    sleep 2
    let COUNTER+=2
    echo "Waiting for mongo to initialize... ($COUNTER seconds so far)"
    grep -q 'waiting for connections on port' /var/log/mongodb.log
done

# Download the dataset
echo "Downloading Dataset"
wget -cO - https://s3.amazonaws.com/reach.lunean.com/iHOP_Full_Dataset_mongo_import_051919.zip > /home/dataset.zip
# Unzip source
echo "Unzip the downloaded Dataset"
unzip /home/dataset.zip -d /home/unzipDestDataset

# Restore from dump
echo "Mongo restore initiated"
mongorestore --drop /home/unzipDestDataset

#delete  source files bash file
echo "Removing temporary files"
rm -rf /home/unzipDestDataset
rm /home/setup.sh
rm /home/dataset.zip

echo "Image is running"
# Keep container running
tail -f /dev/null