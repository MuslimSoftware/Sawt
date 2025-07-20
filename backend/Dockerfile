# Multi-stage build for Rust backend with Whisper.cpp
FROM ubuntu:22.04 as whisper-builder

# Install build dependencies and SSL certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    libgomp1 \
    pkg-config \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/whispercpp

# Clone and build Whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git && \
    cd whisper.cpp && \
    mkdir build && cd build && \
    cmake .. -DGGML_BLAS=OFF -DGGML_OPENBLAS=OFF -DBUILD_SHARED_LIBS=ON && \
    make -j$(nproc) whisper && \
    find . -name "*.so" && \
    cp src/libwhisper.so /usr/local/lib/ && \
    cp ggml/src/libggml.so /usr/local/lib/ && \
    cp ggml/src/libggml-base.so /usr/local/lib/ && \
    cp ggml/src/libggml-cpu.so /usr/local/lib/ && \
    cp ../include/whisper.h /usr/local/include/

# Download Whisper model
RUN mkdir -p /opt/models && \
    cd /opt/models && \
    wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Build stage for Rust
FROM rust:1.78-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    libgomp1 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/whispercpp

# Copy pre-built Whisper libraries from whisper-builder
COPY --from=whisper-builder /usr/local/lib/libwhisper.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml-base.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml-cpu.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/include/whisper.h /usr/local/include/

# Copy Rust app
COPY whispercpp/app ./app

# Copy interface files
COPY whispercpp/interface ./interface

# Build Rust binary
RUN cargo build --manifest-path app/Cargo.toml --release

# Python dependencies stage
FROM python:3.12-slim as python-deps

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 libomp5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 libomp5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/local/lib

# Copy Python environment
COPY --from=python-deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy libraries from whisper-builder
COPY --from=whisper-builder /usr/local/lib/libwhisper.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml-base.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/lib/libggml-cpu.so /usr/local/lib/
COPY --from=whisper-builder /usr/local/include/whisper.h /usr/local/include/

# Copy Whisper model
COPY --from=whisper-builder /opt/models/ggml-base.en.bin /app/models/

# Create symlinks for library versioning
RUN cd /usr/local/lib && \
    ln -sf libwhisper.so libwhisper.so.1 && \
    ln -sf libggml.so libggml.so.1 && \
    ln -sf libggml-base.so libggml-base.so.1 && \
    ln -sf libggml-cpu.so libggml-cpu.so.1 && \
    if [ -d "/usr/lib/aarch64-linux-gnu" ]; then \
        cd /usr/lib/aarch64-linux-gnu && ln -sf libomp.so.5 libgomp.so.1; \
    elif [ -d "/usr/lib/x86_64-linux-gnu" ]; then \
        cd /usr/lib/x86_64-linux-gnu && ln -sf libomp.so.5 libgomp.so.1; \
    else \
        echo "Warning: Could not find OpenMP library directory"; \
    fi

# Copy Rust binary
COPY --from=builder /opt/whispercpp/app/target/release/automation ./automation

# Copy application files
COPY app/ ./app/
COPY configs/ ./configs/
COPY server.py ./
COPY run.py ./

# Expose port
EXPOSE 8000

# Run the Python FastAPI server
CMD ["python", "server.py"]
