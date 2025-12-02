# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose port 8000 (Standard FastAPI)
EXPOSE 8000

# Healthcheck (optional but recommended)
# Note: Change the URL if your app does not have anything on the root "/"
# Now, if the server responds (even with 406 or 404), the check passes.
# If the server is down, curl will give a connection error and the check will fail (correct).
HEALTHCHECK CMD curl --silent --output /dev/null http://localhost:8000/tav/mcp || exit 1


# Start command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]