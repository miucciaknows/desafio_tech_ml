FROM python:3.12.0-slim

WORKDIR /rest_api

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt


EXPOSE 8080


CMD ["python", "main.py"]


