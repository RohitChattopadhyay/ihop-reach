## iHOP-Reach Database container

**Step 1** Pull the image from [Docker Hub](https://hub.docker.com/r/rchattopadhyay/ihop-database)

    docker pull rchattopadhyay/ihop-database

**Step 2** Run the instance using

    docker run -p PORT:27017 rchattopadhyay/ihop-database
Mention the PORT in above command where you wish to expose the image from your localhost
