FROM python:3.12 AS base
ENV PYTHONUNBUFFERED 1

ARG SECRET_KEY

WORKDIR /usr/src/event-management-api

COPY . /usr/src/event-management-api
COPY ./requirements.txt /usr/src/event-management-api
RUN pip install -r requirements.txt

EXPOSE 8000
