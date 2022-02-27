# Pelleum Backend API
This repository contains code relevant to Pelleum's backend API. This API responds to requests sent from Pelleum's frontend mobile application.

## Local Development Instructions

### Setup Virtual Environment
- Run `python3 -m pip install --user --upgrade pip`
- Run `python3 -m pip install --user virtualenv`
- Run `python3 -m venv env`
- Activate virtual environment with `source env/bin/activate`
- Install packages with `python3 -m pip install -r requirements.txt`
- See "Makefile Targets" section for Makefile setup

### Updating Requirements
1. With an activated virtual environment, run `pip freeze > requirements.in`
2. Run `make requirements.txt`

### Migrating Database Schemas
To migrate a new table or make a change to an existing table:
1. Add a new model file or change an existing one found in the [/models](https://github.com/pelleum/pelleum-api/tree/continuous-integration-setup/app/infrastructure/db/models/public) directory
2. Run:
```make migration rev_id=<YOUR REVISION ID> migration_message="your migration message"```
Example:
```make migration rev_id=0002 migration_message="Added payments table"```
  - This will auto-generate alembic files in the [/migrations/versions](https://github.com/pelleum/pelleum-api/tree/master/migrations/versions) directory, which are used for migration
3. From there, provided you have a docker postgreSQL database up and running (`docker-compose up -d db`), you can migrate your changes by running `make migrate`

### Run the API (Locally)
- Install [Docker](https://www.docker.com/)
- Set environment variables in `.env` file in the project's root directory (get from senior engineer)
- Run `docker-compose up -d db` (this spins up a local PostgreSQL database for the API to utilize)
- Run `make run` (this runs server locally)

### Makefile Targets
The following are helpful commands that utilize this project's [Makefile](https://github.com/pelleum/pelleum-api/blob/master/Makefile). To ensure theses work for you, do the following:

1. Install `make`. If on MacOS, you can use [Homebrew](https://formulae.brew.sh/formula/make).
2. Add `alias make='gmake'` to your `bash_profile` (or similar), which you can access at `~/.bash_profile`. After adding this, you'll need to restart your terminal for it to take effect.
3. `make --version` should be **4.3** or higher.

- `make run`: runs the API locally
- `make build`: builds the app's docker image
- `make push`: pushes image to Docker Hub
- `make format`: formats the code using [black](https://black.readthedocs.io/en/stable/) and sorts imports using [isort](https://pycqa.github.io/isort/). Running this target is necessary for continuous integration.
- `make test`: starts continuous integration, which includes running all unit tests
- `make migration`: see "Migrating Database Schemas" section
- `make migrate`: migrates a schema to a target database

## Testing

### Manually Test API Calls
- Can use [Postman](https://www.postman.com/) to test calls (Can get Postman collection from senior engineer)
- Can also test calls via [API Docs](http://0.0.0.0:8000/docs)

### Continuous Integration
As mentioned above, continuous integration is initiated by running `make test`. Running this command will:

1. Spin up the application's docker container a test postgreSQL database docker container for tests to utilize
2. Lint the code using Pylint
3. Check the code's format
4. Configure the newly spun up database
5. Run unit tests

**Note:** These docker containers utilize a `tests.env` file.

### Run Unit Tests Manually
Unit tests can be run manually by running `invoke tests` or by running them individually using your IDE. Before running them, be sure to:
1. Spin up the test postgreSQL docker container by running `docker-compose up -d test_db`
2. Create `account_connections` schema using PgAdmin or by running: `CREATE SCHEMA account_connections`.
3. Migrate database tables by running `alembic upgrade head` (you can temporarily change the database URL in the [env.py](https://github.com/pelleum/pelleum-api/blob/master/migrations/env.py) file to run alembic against the test database)

## Deployment

### Push Image to Docker Hub
- Run `docker login`, get credentials from Bitwarden
- Run `docker build -t pelleum/pelleum-api .` (or `make build`) to build the docker image
- Run `docker push pelleum/pelleum-api` (or `make push`) to push the image to Docker Hub
- Verify that the image has been updated in Docker Hub

### Deploy Cluster in AWS
- Update pelleum-api service in AWS console
- Make sure to use latest version and check the "Force new deployment" box
- Verify by viewing logs in CloudWatch
