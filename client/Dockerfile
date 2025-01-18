FROM python:3.9-slim

RUN pip install requests

COPY client.py /app/client.py
WORKDIR /app

CMD ["python", "client.py"]