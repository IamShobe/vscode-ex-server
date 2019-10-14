FROM python:3.7-alpine

WORKDIR /app

RUN apk --update add openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev build-base libxslt-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD gunicorn -c gunicorn.conf.py main:app --access-logfile '-'
