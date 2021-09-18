SHELL := bash

docker_image = pelleum_api
docker_username = adamcuculich
python_code := app/ migrations/


requirements.txt:
	pip-compile --generate-hashes --output-file=requirements.txt requirements.in

black:
	black $(python_code)

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

