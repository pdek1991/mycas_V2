# Use official Python Alpine image
FROM python:3.9-alpine3.20

# Set environment variables to avoid creating .pyc files and to force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /mycas/CLIENT

# Copy only the requirements file first (for better Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Ensure the correct permissions for execution
RUN chmod +x stb_client.py

# Use a non-root user for security (optional, but recommended)
RUN addgroup -S mycas && adduser -S mycas -G mycas
USER mycas

# Default command to run the application
CMD ["python", "stb_client.py"]