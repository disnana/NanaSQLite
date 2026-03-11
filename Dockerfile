FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml setup.cfg* ./
RUN uv pip install --system \
    pytest pytest-benchmark pytest-asyncio \
    apsw pydantic cryptography orjson

COPY . .
RUN uv pip install --system -e ".[dev]"
