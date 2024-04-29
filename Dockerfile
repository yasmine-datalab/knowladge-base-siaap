FROM apache/airflow:latest
LABEL maintainer="Data354"
#Ce paramètre empêche le masquage des erreurs dans un pipeline
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
USER root
RUN apt-get update -y && apt-get install -y  build-essential && python -m pip install --upgrade pip
USER airflow
COPY requirements.txt .
RUN pip install -r requirements.txt