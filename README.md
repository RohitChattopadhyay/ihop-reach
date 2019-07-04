## iHOP-Reach REST API container

For GraphQL based API use [`docker-api`](https://github.com/RohitChattopadhyay/ihop-reach/tree/docker-api) branch.  


**Step 1** Build the Docker image using

    docker-compose build

You may change the PORT in the `docker-compose.yml` file

**Step 2** Run the instance using

    docker-compose up
    
   Consume the API at `localhost:5000` or `localhost:PORT` , if you have changed the port.
