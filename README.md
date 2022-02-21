# Pelleum Backend API
This repository contains code relevant to Pelleum's backend API. This API responds to requests sent from Pelleum's frontend mobile application.

## Local Development Instructions

## Setup virtual environment
- Run `python3 -m pip install --user --upgrade pip`
- Run `python3 -m pip install --user virtualenv`
- Run `python3 -m venv env`
- Activate virtual environment with `source env/bin/activate`
- Install packages with `python3 -m pip install -r requirements.txt`

## Run the API
- Install Docker
- Set environment variables in `.env` file in the project's root directory (get from senior engineer)
- Run `docker-compose up -d db` (this spins up a local PostgreSQL database for the API to utilize)
- Run `make run` (this runs server locally)
- Can stop docker container by running `docker stop <CONTAINER ID>`; the `CONTAINER_ID` can be found by running `docker ps`

## Test API Calls
- Can use Postman to test calls (Can get Postman collection from senior engineer)
- Can also test calls via [API Docs](http://0.0.0.0:8000/docs)

## Push Image to Docker Hub
- Run `docker login`, get credentials from Bitwarden
- Run `docker build -t pelleum/pelleum-api .` to build the docker image
- Run `docker push pelleum/pelleum-api` to push the image to Docker Hub
- Verify that the image has been updated in Docker Hub

## Deploy Cluster in AWS
- Update pelleum-api service in AWS console
- Make sure to use latest version and check the "Force new deployment" box
- Verify by viewing logs in CloudWatch
