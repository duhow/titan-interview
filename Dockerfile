# syntax=docker/dockerfile:1.27-labs

ARG PYTHON_VERSION=3.14.7
ARG BASE_IMAGE=docker.io/library/python:${PYTHON_VERSION}-slim
FROM ${BASE_IMAGE} AS base

ENV DEBIAN_FRONTEND=noninteractive
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt update && \
    apt upgrade -y && \
    apt install --no-install-recommends -y \
      ca-certificates \
    && useradd --uid 1001 --create-home app

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.1.0 /lambda-adapter /opt/extensions/lambda-adapter

# -- Optimize image copy by squashing updated apps/libs
FROM scratch AS build
COPY --link --from=base / /
# -----

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache,rw \
    pip install --no-compile -r requirements.txt

COPY app/ ./app/
COPY alembic.ini ./
COPY alembic/ ./alembic/

RUN mkdir /data && chown app:app /data

USER app

VOLUME ["/data"]

ENV PORT=8000 AWS_LWA_READINESS_CHECK_PATH=/healthz/startup
EXPOSE ${PORT}
CMD ["sh", "-c", "alembic upgrade head && exec fastapi run app/main.py"]
