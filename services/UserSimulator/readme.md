# Cofoundrie Interview Project - Release 1

This is the foundation milestone.  
It sets up a simple FastAPI service, containerized with Docker.

## Run locally
```bash
# go to the UserSimulator service
cd services/UserSimulator

# build the image
docker build -t user-simulator .

# run the container
docker run -p 8080:8080 user-simulator
