FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    protobuf-compiler \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/image_generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install grpcio-tools for protobuf compilation
RUN pip install --no-cache-dir grpcio-tools

# Copy protobuf definitions
COPY src/lib_py/gen_types/ /tmp/protos/

# Generate Python code from protobuf definitions
RUN python -m grpc_tools.protoc -I/tmp/protos/ --python_out=/tmp/protos/ /tmp/protos/*.proto

# Copy application code
COPY src/image_generator/main.py /app/src/image_generator/
COPY src/lib_py /app/src/lib_py

# Copy generated protobuf files
RUN cp -r /tmp/protos/* /app/src/lib_py/gen_types/

# Set environment variables
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --spider -q http://localhost:8080/healthz || exit 1

# Run the application
CMD ["python", "src/image_generator/main.py"]
