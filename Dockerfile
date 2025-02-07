FROM python:3.11.6-alpine3.18
LABEL maintainer="dima.kolhac@gmail.com"

ENV PYTHONBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN mkdir -p /weather_data
RUN mkdir -p /logs && chmod -R 777 /logs