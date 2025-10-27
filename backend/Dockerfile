#checkov:skip=CKV_DOCKER_9: Allow for use of apt
#checkov:skip=CKV_DOCKER_2: No need for healthcheck in container
#checkov:skip=CKV_DOCKER_3: No need for user in container
#checkov:skip=CKV_DOCKER_7: Allow the base image to use the latest version tag
FROM debian:12-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev git && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools wheel

FROM build AS build-venv
COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

FROM gcr.io/distroless/python3-debian12
COPY --from=build-venv /venv /venv
WORKDIR /app

COPY api api
COPY static static

ARG commit_sha
ENV COMMIT_SHA=$commit_sha

ARG version
ENV VERSION=$version

ENTRYPOINT ["/venv/bin/python3", "-m", "uvicorn", "api.entry:app", "--host", "0.0.0.0", "--port", "8000"]
