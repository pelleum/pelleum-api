FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Database Environment Variables
ENV DB_URL=postgres://postgres:postgres@localhost:5432/pelleum-dev
ENV SCHEMA=nope

# JWT Environment Variables
ENV JSON_WEB_TOKEN_SECRET=nicetry

# Auth Environment Variables
ENV TOKEN_URL=/public/auth/users/login
ENV ACCESS_TOKEN_EXPIRE_MINUTES=120.0
ENV JSON_WEB_TOKEN_ALGORITHM=nope

# Environment Environment Variables
ENV OPENAPI_URL="/openapi.json"

# Pelleum API port
ENV SERVER_PORT=8000

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]