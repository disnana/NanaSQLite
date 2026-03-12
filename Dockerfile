FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv==0.10.2

COPY pyproject.toml setup.cfg* uv.lock* ./

RUN uv pip install --system --no-cache \
    pytest pytest-benchmark pytest-asyncio \
    apsw pydantic cryptography orjson

COPY . .

RUN uv pip install --system --no-cache ".[dev]"
