FROM python:3.10
LABEL maintainer='Mikhail Nikolaev'

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt /average_forecast/
WORKDIR /average_forecast
EXPOSE 8000

RUN pip install --upgrade pip && pip install -r requirements.txt 

COPY . /average_forecast/