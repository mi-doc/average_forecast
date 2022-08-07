FROM python:3.10-slim as builder
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip setuptools wheel

WORKDIR /wheels
COPY requirements.txt /requirements.txt
RUN pip wheel -r /requirements.txt


FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY --from=builder /wheels /wheels
RUN pip install -U pip setuptools wheel \
        && pip install /wheels/* \
        && rm -rf /wheels \
        && rm -rf /root/.cache/pip/* \
        && mkdir logs staticfiles \
        && touch logs/celery.log \
        && adduser --disabled-password --no-create-home app \
        && chown -R app:app logs/ staticfiles/ \
        && chmod -R 755 logs/ staticfiles/

COPY . .

EXPOSE 8000
ENV PYTHONPATH /code

USER app