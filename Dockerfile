FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Database Environment Variables
ENV DB_USERNAME=postgres
ENV DB_PASSWORD=postgres
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=db_name
ENV DB_ENGINE=postgres

# JWT Environment Variables
ENV JSON_WEB_TOKEN_SECRET=nicetry

# Non-secret Environment Variables
ENV TOKEN_URL=/public/auth/users/login
ENV ACCESS_TOKEN_EXPIRE_MINUTES=120.0
ENV JSON_WEB_TOKEN_ALGORITHM=Something
ENV SCHEMA=Something


# Pelleum API port
ENV PORT=8000

EXPOSE $PORT

CMD ["python", "-m", "app"]