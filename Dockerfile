FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

ENV DB_USERNAME=somusername123
ENV DB_PASSWORD=sompassword456
ENV DB_ENGINE=postgres
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=my_db_name
ENV JSON_WEB_TOKEN_SECRET=asflkasdf$ladjksf42423l4k34ln^899kjadf

CMD ["python", "-m", "app"]