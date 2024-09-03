FROM python:3.10-slim AS base

RUN apt-get update && apt-get install -y git ffmpeg && apt-get clean
RUN pip install uvicorn

FROM base AS cuda_dependencies

COPY venv/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages/

FROM base AS final

COPY --from=cuda_dependencies /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=cuda_dependencies /usr/local/bin /usr/local/bin

COPY . /app
WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["sh", "-c", ". /app/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"]

