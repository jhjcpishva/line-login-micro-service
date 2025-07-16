# === Build stage ===
FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

# === Final stage ===
FROM python:3.13-alpine
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/line-login-micro-service"

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . /app

CMD ["python", "main.py"]
