FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    protobuf-compiler \
    wget \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY src/text_overlay/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install grpcio-tools for protobuf compilation
RUN pip install --no-cache-dir grpcio-tools

# Copy protobuf definitions
COPY proto/ /tmp/protos/

# Compile protobufs
RUN python -m grpc_tools.protoc -I/tmp/protos/ --python_out=/tmp/protos/ /tmp/protos/*.proto

# Fix imports to use relative imports
RUN cd /tmp/protos && for file in *_pb2.py; do sed -i "s/^import \(.*\)_pb2 as/from . import \1_pb2 as/g" "$file"; done

# Copy application code
COPY src/text_overlay/main.py /app/src/text_overlay/
COPY src/lib_py /app/src/lib_py

# Copy compiled protobufs to lib_py
RUN cp -r /tmp/protos/* /app/src/lib_py/gen_types/

# Set Python path
ENV PYTHONPATH=/app

# Run the service
CMD ["python", "-u", "src/text_overlay/main.py"]
