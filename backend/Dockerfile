FROM python:3.12-slim

WORKDIR /app

# System dependencies for Whisper + audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.docker.txt .
RUN pip install --no-cache-dir "setuptools<71" wheel && \
    pip install --no-cache-dir --no-build-isolation openai-whisper==20240930 && \
    pip install --no-cache-dir -r requirements.docker.txt

# Copy backend source
COPY backend/ ./backend/

# Copy pre-built FAISS index and raw source files
COPY . /build_context/
RUN cp -r /build_context/data ./data 2>/dev/null || mkdir -p ./data && \
    cp -r /build_context/raw_data ./raw_data 2>/dev/null || true && \
    rm -rf /build_context

ENV PYTHONUNBUFFERED=1

COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["/entrypoint.sh"]
