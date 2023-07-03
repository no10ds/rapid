FROM python:3.10-slim

WORKDIR /app
RUN apt update
RUN apt install -y git

COPY requirements.txt .
RUN pip install -r requirements.txt


ARG commit_sha
ENV COMMIT_SHA=$commit_sha

ARG version
ENV VERSION=$version
