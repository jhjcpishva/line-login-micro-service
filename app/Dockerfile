FROM python:3.11-slim
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/line-messaging-micro-service"

EXPOSE 8000

RUN mkdir /app/
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
CMD ["python", "main.py"]

