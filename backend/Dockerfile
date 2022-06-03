FROM python:3.10 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/groceryaid

FROM base AS builder

RUN set -ex; pip install poetry==1.1.13; python -m venv /usr/venv/groceryaid

COPY pyproject.toml poetry.lock ./
RUN poetry export | /usr/venv/groceryaid/bin/pip install -r /dev/stdin

COPY . .
RUN set -ex; poetry build; /usr/venv/groceryaid/bin/pip install dist/*.whl

FROM base

EXPOSE 8000

COPY start.sh alembic.ini ./
COPY alembic ./alembic
COPY --from=builder /usr/venv /usr/venv

ENTRYPOINT ["./start.sh"]
CMD ["gunicorn", "--forwarded-allow-ips", "*", "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "groceryaid:app"]
