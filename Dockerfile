FROM python:3.12-slim

WORKDIR /app

# Install system dependencies that may be needed by Pillow, pydicom, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the app
RUN useradd -m -u 1000 corpususer && chown -R corpususer:corpususer /app

# Install Python dependencies
COPY --chown=corpususer:corpususer requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=corpususer:corpususer . .

USER corpususer

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
