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

- Create namespace  
  
  `create namespace mlops-prefect`

- Add prefect helm repo  
  
  `helm repo add prefect https://prefecthq.github.io/prefect-helm`

- Search prefect helm repo  
  
  `helm search repo prefect`

- Install prefect server in created namespace using custom values    
  
  `helm install prefect-server prefect/prefect-server -n mlops-prefect -f prefect/values_server.yaml --version 2023.04.13`

### Configure a client to use the server

- Install prefect in the client  
  
  `pip install prefect==2.10.4 prefect-kubernetes==0.2.4`

- Create server profile and modify api url parameter  
  
  `prefect profile create server`  

  `prefect profile use 'server' `   

  `prefect config set PREFECT_API_URL="http://192.168.219.33:<PREFECT-API-PORT>/api"`

### Create useful blocks

- Execute the file `init_blocks.py`, which creates useful blocks (MinIO user and password has to be added first).  
  
  `python prefect/init_blocks.py`

- Create a work pool for sending flows that will be executed in Kubernetes
  
  `prefect work-pool create k8s-pool`

- Create a deployment for the testing flow using the K8s infrastructure (should be similar to the one in guthub `test_flow_deployment.yaml`)   
  
  `prefect deployment build -n test-flow-deployment-k8s -p k8s-pool -ib kubernetes-job/k8s-infra -sb s3/khaos-minio  -o test_flow_deployment.yaml test_flow.py:my_flow`  

  `prefect deployment apply test_flow_deployment.yaml`

- Create a quick run of the deployment using the UI and check if the flow is succesfully executed (an agent have to be created first)

  `prefect agent start --pool k8s-pool --work-queue default`