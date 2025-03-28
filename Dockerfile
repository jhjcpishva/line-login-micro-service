FROM python:3.13-slim
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/line-messaging-micro-service"

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only necessary files first to leverage caching
COPY pyproject.toml uv.lock /app/

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application files
COPY . /app

# Run the application
CMD ["uv", "run", "main.py"]
