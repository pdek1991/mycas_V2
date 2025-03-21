# --- Stage 1: Build dependencies and obfuscate Python code ---
    FROM python:3.10 AS builder  
    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # Set working directory
    WORKDIR /mycas/WEB-APP
    
    # Install system dependencies (Debian-based)
    RUN apt-get update && apt-get install -y \
        build-essential libssl-dev libffi-dev python3-dev \
        librdkafka-dev  
    
    # Copy only requirements.txt to use Docker's caching feature
    COPY requirements.txt . 
    
    # Install dependencies in a virtual environment
    RUN python -m venv /opt/venv \
        && /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
        && /opt/venv/bin/pip install --no-cache-dir confluent-kafka -r requirements.txt
    
    # Copy application files
    COPY . .
    
    # Ensure the output directory exists before obfuscation
    RUN mkdir -p /mycas/WEB-APP/dist
    
    # Obfuscate Python code using PyArmor
    RUN /opt/venv/bin/pyarmor gen -O /mycas/WEB-APP/dist webpage.py
    
    # Clean up to reduce image size
    RUN apt-get remove -y build-essential python3-dev libffi-dev \
        && apt-get autoremove -y \
        && rm -rf /var/lib/apt/lists/*
    
    # --- Stage 2: Create a minimal runtime image ---
    FROM python:3.10-slim  
    
    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PATH="/opt/venv/bin:$PATH"
    
    # Set working directory
    WORKDIR /mycas/WEB-APP
    
    # ✅ Install only runtime dependencies
    RUN apt-get update && apt-get install -y \
        librdkafka1  
    
    # Create a non-root user for security
    RUN groupadd -r mycas && useradd -r -g mycas mycas
    
    # Copy only the virtual environment from the builder stage
    COPY --from=builder --chown=mycas:mycas /opt/venv /opt/venv
    
    # Copy only the obfuscated Python files (not the original source code)
    COPY --from=builder --chown=mycas:mycas /mycas/WEB-APP/dist /mycas/WEB-APP/
    RUN mkdir -p /mycas/WEB-APP/Logs && \
    chown -R mycas:mycas /mycas/WEB-APP && \
    chmod -R 770 /mycas/WEB-APP && \
    chmod -R 770 /mycas/WEB-APP/Logs


    COPY templates/index.html templates/index.html
    
    # Ensure correct file permissionsc
    USER mycas
    
    # Use ENTRYPOINT for better flexibility
    ENTRYPOINT ["python", "/mycas/WEB-APP/webpage.py"]
    