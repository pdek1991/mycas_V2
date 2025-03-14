# --- Stage 1: Build dependencies and obfuscate Python code ---
    FROM python:3.10-alpine AS builder

    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # Set working directory
    WORKDIR /mycas/CYCLER
    
    # Install required system packages
    RUN apk add --no-cache \
        python3-dev py3-pip \
        build-base libffi-dev musl-dev
    
    # Install dependencies in a virtual environment
    COPY requirements.txt .
    RUN python -m venv /opt/venv \
        && /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
        && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
    
    # Install PyArmor for obfuscation
    RUN /opt/venv/bin/pip install --no-cache-dir pyarmor
    
    # Copy application files
    COPY . .
    
    # Ensure the output directory exists before obfuscation
    RUN mkdir -p /mycas/CYCLER/dist
    
    # Obfuscate Python code using PyArmor
    #RUN /opt/venv/bin/pyarmor pack -x " --exclude dist" -O /mycas/CYCLER/dist stb_CYCLER.py
    RUN /opt/venv/bin/pyarmor gen -O /mycas/CYCLER/dist cycler.py
    
    # Remove unnecessary build dependencies to reduce size
    RUN apk del build-base libffi-dev musl-dev
    
    # --- Stage 2: Create a minimal runtime image ---
    FROM python:3.10-alpine
    
    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PATH="/opt/venv/bin:$PATH"
    
    # Set working directory
    WORKDIR /mycas/CYCLER
    
    # Install only necessary runtime dependencies
    RUN apk add --no-cache libffi
    
    # Create a non-root user for security
    RUN addgroup -S mycas && adduser -S mycas -G mycas
    
    # Copy only the virtual environment from the builder stage
    COPY --from=builder --chown=mycas:mycas /opt/venv /opt/venv
    
    # Copy only the obfuscated Python files (not the original source code)
    COPY --from=builder --chown=mycas:mycas /mycas/CYCLER/dist /mycas/CYCLER/
    COPY stage_cycle.ini stage_cycle.ini
    
    # Ensure correct file permissions
    USER mycas
    
    # Use ENTRYPOINT for better flexibility
    ENTRYPOINT ["python", "/mycas/CYCLER/cycler.py"]
    