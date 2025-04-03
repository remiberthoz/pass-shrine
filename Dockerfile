FROM python:3.14.0a6-alpine3.21
RUN apk add age gpg
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "main"]
