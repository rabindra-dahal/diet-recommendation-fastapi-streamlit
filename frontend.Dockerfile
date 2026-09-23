# Use a slim, official Python runtime base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install explicit frontend dependencies 
RUN pip install --no-cache-dir streamlit requests matplotlib pandas

# Copy application layers
COPY frontend/ /app/frontend/
COPY main_frontend.py /app/main_frontend.py

# Expose native Streamlit port
EXPOSE 8501

# Streamlit network routing adjustments to work inside isolated network clusters
CMD ["streamlit", "run", "main_frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
