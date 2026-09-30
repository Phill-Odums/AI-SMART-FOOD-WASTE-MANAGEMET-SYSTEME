# Use an official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for PostgreSQL and package compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverages Docker layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . /app/

# Normalize line endings and make entrypoint executable
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port (Render overrides this with $PORT, default 8000/10000)
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

