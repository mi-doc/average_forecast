FROM python:3.10-slim as builder
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip setuptools wheel

WORKDIR /wheels
COPY average_forecast/requirements.txt /requirements.txt
RUN pip wheel -r /requirements.txt


FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY --from=builder /wheels /wheels
RUN pip install -U pip setuptools wheel \
        && pip install /wheels/* \
        && rm -rf /wheels \
        && rm -rf /root/.cache/pip/* 

COPY . .

RUN mkdir -p average_forecast/{logs,staticfiles} /home/app \
        && touch average_forecast/logs/celery.log \
        && adduser --disabled-password --no-create-home app \
        && chown -R app:app average_forecast/{logs,staticfiles} /home/app/ \
        && chmod -R 755 average_forecast/{logs,staticfiles}

EXPOSE 8000
ENV PYTHONPATH /code

USER app