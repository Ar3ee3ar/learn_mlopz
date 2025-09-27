FROM python:3.9-slim

# # Copy in the uv binary from the official UV image at a specific version tag.
# COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /bin/uv
# ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN apt update && \
    apt install -y \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY app.py .
COPY pyproject.toml /app/
# COPY .env .
# COPY models/ ./models/

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]

