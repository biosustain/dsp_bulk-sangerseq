FROM python:3.12

ARG NXF_VER=25.10.4

ENV DEBIAN_FRONTEND=noninteractive \
    NXF_HOME=/opt/nextflow \
    PATH="/opt/nextflow:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl openjdk-21-jre-headless git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://github.com/nextflow-io/nextflow/releases/download/v${NXF_VER}/nextflow -o /opt/nextflow/nextflow \
    && chmod +x /opt/nextflow/nextflow

RUN pip install --no-cache-dir pipenv==2025.0.4

WORKDIR /workspace

CMD ["nextflow", "-version"]
