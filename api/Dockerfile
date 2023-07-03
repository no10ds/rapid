FROM python:3.10-slim

WORKDIR /app
RUN apt update
RUN apt install -y git
RUN apt install -y gcc
RUN apt install -y g++

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY api api
COPY static static

ARG commit_sha
ENV COMMIT_SHA=$commit_sha

ARG version
ENV VERSION=$version

CMD ["uvicorn", "api.entry:app", "--host", "0.0.0.0", "--port", "8000"]
