FROM python:3.9-slim

RUN pip install flask

COPY server.py /app/server.py

WORKDIR /app

EXPOSE 5000

CMD ["python", "server.py"]
