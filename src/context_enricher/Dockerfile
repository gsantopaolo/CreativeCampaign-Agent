FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY src/context_enricher/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY src/context_enricher/main.py /app/src/context_enricher/main.py

# Copy shared lib
COPY src/lib_py /app/src/lib_py

# Set Python path
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/context_enricher/main.py"]
