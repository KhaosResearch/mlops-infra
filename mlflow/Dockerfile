FROM python:3.11.3

LABEL org.opencontainers.image.source=https://github.com/KhaosResearch/mlops-infra/
LABEL org.opencontainers.image.description="Mlflow deployment image"
LABEL org.opencontainers.image.licenses=MIT

RUN apt update && apt install -y python3-venv gcc
RUN apt-get install -y python3-dev build-essential

ENV VENV=/.venv/myenv
RUN python3 -m venv ${VENV}
RUN mkdir -p $VENV/src
ENV PATH=$VENV/bin:$PATH
RUN pip install -U pip
RUN pip install "psycopg2==2.9.6" "sphinx==5.3.0" "mlflow==2.3.1" "s3==3.0.0" "boto3==1.26.129"

# Expose the port that the MLFlow tracking server runs on
EXPOSE 5000

ENTRYPOINT mlflow server \
        --default-artifact-root s3://$MLFLOW_S3_BUCKET \
        --backend-store-uri postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_URL/$DB_NAME --host 0.0.0.0
