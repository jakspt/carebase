
FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc pkg-config default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 5000


CMD ["gunicorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]