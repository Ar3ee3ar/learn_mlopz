# stage: 1 Base build 
FROM python:3.10-slim AS builder

# install necessary library
RUN apt update && \
    apt install -y \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# select work directory
WORKDIR /app

# Set environment variable
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYCODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# copy api file
# COPY app.py .
# COPY pyproject.toml /app/
# COPY .env .
# COPY models/ ./models/

# Copy requirements
COPY requirements.txt .
# 
# RUN pip install --upgrade pip setuptools wheel && \
# install python lib
RUN pip install --no-cache-dir -r requirements.txt
# Expose port

# stage2 : production stage
FROM python:3.10-slim

# security
RUN apt install adduser && \
    useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Set environment variable
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYCODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# define work directory
WORKDIR /app

# Copy python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin /usr/local/bin

# copy project to the container
COPY --chown=appuser app.py .

# switch to non-root user
USER appuser

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

