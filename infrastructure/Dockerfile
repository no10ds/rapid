#checkov:skip=CKV_DOCKER_9: Allow for use of apt
#checkov:skip=CKV_DOCKER_2: No need for healthcheck in container
#checkov:skip=CKV_DOCKER_3: No need for user in container
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
