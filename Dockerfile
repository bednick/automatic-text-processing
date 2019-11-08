FROM python:3.6.9-stretch

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /project
