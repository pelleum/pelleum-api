SHELL := /bin/bash

docker_image = pelleum-api
docker_username = pelleum
formatted_code := app/ migrations/ tests/ tasks.py
rev_id = ""
migration_message = ""

.ONESHELL:

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --output-file=$@

format:
	isort $(formatted_code)
	black $(formatted_code)

lint:
	pylint app

run:
	python -m app --reload

make run-container:
	docker-compose up -d

check:
	black --check $(formatted_code)

build:
	docker build -t $(docker_username)/$(docker_image):latest .


# Stop and tear down any containers after tests run
test: build
	function removeContainers {
		docker-compose -p pelleum-api-continuous-integration rm -s -f test_db
	}
	trap removeContainers EXIT
	docker-compose -p pelleum-api-continuous-integration run --rm continuous-integration

push:
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
