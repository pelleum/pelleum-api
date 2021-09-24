SHELL := /bin/bash

docker_image = pelleum_api
docker_username = adamcuculich
python_code := app/ migrations/

requirements.txt:
	pip-compile --generate-hashes --output-file=requirements.txt requirements.in

black:
	black $(python_code)

lint:
	pylint app

run-dev:
	python -m app --reload

check:
	black --check $(python_code)

build:
	docker build -t $(docker_image):latest .

test:
	docker run $(docker_image):latest \
		black --check $(python_code)

push:
	# check to make sure this is correct ...
	docker push $(docker_username)/$(docker_image):latest

generate-migrations:
	alembic -x db_url=postgresql://postgres:postgres@localhost:5432/pelleum-dev revision --autogenerate --rev-id "0001" -m "Initial users schema added"

migrate:
	alembic -x db_url=postgresql://postgres:postgres@localhost:5432/pelleum-dev upgrade "0001"
