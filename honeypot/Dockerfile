FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY honeypot.py .
COPY static/ ./static/
COPY templates/ ./templates/ 

RUN mkdir -p /app/logs

EXPOSE 8080

CMD ["python", "-u", "honeypot.py"]