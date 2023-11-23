FROM python:3.11.3


RUN pip install poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    python3-dev \
    gcc \
    python3-psycopg2 \
    tzdata \
    gettext \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-dev

ADD . /app/
EXPOSE 5001

ENTRYPOINT ["python" , "app.py"]
