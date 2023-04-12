FROM python:3.8.10
RUN apt update && apt install -y python3-venv gcc
RUN apt-get install -y python3-dev build-essential

ENV VENV=/.venv/myenv
RUN python3 -m venv ${VENV}
RUN mkdir -p $VENV/src
ENV PATH=$VENV/bin:$PATH
RUN pip install -U pip
RUN pip install psycopg2 "mlflow>=1.30.0,<2.0" s3 boto3

# Expose the port that the MLFlow tracking server runs on
EXPOSE 5000

ENTRYPOINT mlflow server \
        --default-artifact-root s3://$MLFLOW_S3_BUCKET \
        --backend-store-uri postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_URL/$DB_NAME --host 0.0.0.0
