#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p src/lib_py/gen_types

# Compile all .proto files
for proto_file in $(find src/lib_py/gen_types -name "*.proto"); do
  echo "Compiling $proto_file..."
  python -m grpc_tools.protoc \
    -I=src/lib_py/gen_types \
    --python_out=src/lib_py/gen_types \
    $proto_file
  
  # Generate _pb2_grpc.py files for gRPC services
  if grep -q "service" "$proto_file"; then
    python -m grpc_tools.protoc \
      -I=src/lib_py/gen_types \
      --grpc_python_out=src/lib_py/gen_types \
      $proto_file
  fi
done

echo "Protobuf compilation complete!"
