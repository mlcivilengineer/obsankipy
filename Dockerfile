# Dockerfile for the project
FROM python:3.10.13-alpine
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./src /app
CMD ["python", "obsankipy.py", "config.yaml"]