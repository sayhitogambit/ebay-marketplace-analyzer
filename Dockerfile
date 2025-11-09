FROM python:3.11-slim
WORKDIR /app
COPY ../../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt beautifulsoup4
COPY ../../shared /app/shared
COPY . /app/actor
WORKDIR /app/actor
RUN mkdir -p /app/output
ENV PYTHONUNBUFFERED=1 OUTPUT_DIR=/app/output
CMD ["python", "main.py"]
