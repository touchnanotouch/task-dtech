# Stage 1

FROM python:3.13-slim AS builder

WORKDIR /build

COPY pyproject.toml .

RUN mkdir -p app && touch app/__init__.py && \
    pip install --no-cache-dir .

# Stage 2

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN pip install --no-cache-dir --no-deps .

EXPOSE 8000

CMD ["sanic", "app.core.factory:create_app", "--host=0.0.0.0", "--port=8000", "--single-process"]
