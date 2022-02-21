# Pelleum Backend API
This repository contains code relevant to Pelleum's backend API. This API responds to requests sent from Pelleum's frontend mobile application.

## Local Development Instructions

## Setup virtual environment
- Run `python3 -m pip install --user --upgrade pip`
- Run `python3 -m pip install --user virtualenv`
- Run `python3 -m venv .venv`
- Activate virtual environment with `source .venv/bin/activate`
- Install packages with `python3 -m pip install -r requirements.txt`

## Run docker container
- Install docker
- Set environment variables in .env file (get from senior engineer)
- Run `docker-compose up -d db`
- Run `make run`
- Can stop docker container by running `docker stop <CONTAINER ID>`, CONTAINER_ID can be found by running `docker ps`

## Test API calls
- Can use Postman to test calls (Can get Postman collection from senior engineer)
- Can also test calls via [API Docs](http://0.0.0.0:8000/docs)