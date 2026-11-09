FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY analytics ./analytics
COPY api ./api
COPY dashboard ./dashboard
COPY artifacts ./artifacts

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]