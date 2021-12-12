SHELL := /bin/bash

docker_image = pelleum_api
docker_username = adamcuculich
python_code := app/ migrations/
rev_id = ""
migration_message = ""

.ONESHELL:

requirements.txt:
	pip-compile --generate-hashes --output-file=requirements.txt requirements.in

format:
	isort --profile black $(python_code)
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

migration:
	if [ -z $(rev_id)] || [ -z $(migration_message)]; \
	then \
		echo -e "\n\nmake migration requires both a rev_id and a migration_message.\nExample usage: make migration rev_id=0001 migration_message=\"my message\"\n\n"; \
	else \
		alembic revision --autogenerate --rev-id "$(rev_id)" -m "$(migration_message)"; \
	fi

migrate:
	alembic upgrade head
