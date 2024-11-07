FROM python:3.11-slim

# ENV PORT=80 初期値

RUN mkdir /app/
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
# CMD ["sh", "-c", "uvicorn main:app --port ${PORT}"]
CMD ["python", "main.py"]

