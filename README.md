# MLOps Infrastructure

This repository contains a set of files for deploying an MLOps environment on Kubernetes, with the following services:

- **MLflow**: for model registry.
- **PostgreSQL**: required by MLflow to store metadata.
- **Seldon Core**: for model deployment.
- **Prefect**: for pipeline management.
- **MinIO**: for object storage.
- Maybe **Prometheus** will be added


## MLflow installation


## Seldon Core installation


## Prefect Server installation

[Helm chart repo](https://github.com/PrefectHQ/prefect-helm/tree/main)

Versions:

- Python 3.11.3
- Prefect chart 2023.04.13
- Prefect 2.10.4

### How to deploy server in K8s:

`create namespace mlops-prefect`

`helm repo add prefect https://prefecthq.github.io/prefect-helm`

`helm search repo prefect`

`helm install prefect-server prefect/prefect-server -n mlops-prefect -f prefect/values_server.yaml --version 2023.04.13`