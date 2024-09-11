FROM python:3.10-slim AS base

# Install necessary packages including SQLite and ffmpeg
RUN apt-get update && apt-get install -y git ffmpeg sqlite3 && apt-get clean

ENV COQUI_LICENSE_AGREEMENT="y"
ENV DB_PATH=/app/db/voiceRecord.sqlite
# Install Uvicorn for running FastAPI
RUN pip install uvicorn rich 

# Stage for CUDA dependencies (if needed)
FROM base AS cuda_dependencies

# Copy Python packages from the venv
COPY venv/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages/

# Final stage
FROM base AS final

# Copy dependencies from the cuda stage
COPY --from=cuda_dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=cuda_dependencies /usr/local/bin /usr/local/bin

# Copy the application code
COPY . /app
WORKDIR /app

# Expose the port FastAPI will run on
EXPOSE 8000

ENTRYPOINT ["sh", "-c", ". /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"]

