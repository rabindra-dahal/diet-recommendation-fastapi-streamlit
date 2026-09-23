# Use a slim, official Python runtime base
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for compiling C extensions if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirement streams
COPY .env /app/.env
RUN pip install --no-cache-dir fastapi uvicorn google-genai numpy python-dotenv pydantic

# Copy backend submodules and core runner script
COPY backend/ /app/backend/
COPY main_backend.py /app/main_backend.py

# Expose production Uvicorn socket port
EXPOSE 8000

# Fire up the REST engine
CMD ["uvicorn", "main_backend:app", "--host", "0.0.0.0", "--port", "8000"]
