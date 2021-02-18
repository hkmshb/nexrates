FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10
LABEL maintainer="Abdul-Hakeem Shaibu <hkmshb@gmail.com>"

ENV MODULE_NAME="nexrates"

# Install OS packages in order to rebuild latest versions of
# gino and uvicorn and their respective dependencies ...
RUN apk add --no-cache --virtual .build-deps curl gcc libc-dev make

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python \
    && cd /usr/local/bin \
    && ln -s /opt/poetry/bin/poetry \
    && poetry config virtualenvs.create false

# Copy App resources
COPY pyproject.toml poetry.lock* /app/
COPY nexrates /app/nexrates

# Install App dependencies
RUN python -m pip install --upgrade pip \
    && poetry install --no-root --no-dev
