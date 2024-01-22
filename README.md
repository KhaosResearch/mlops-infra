# MLOps Infrastructure

This repository contains a set of files for deploying an MLOps environment on Kubernetes, with the following services:

- **MLflow**: for model registry.
- **PostgreSQL**: required by MLflow to store metadata.
- **Seldon Core**: for model deployment.
- **Prefect**: for pipeline management.
- **MinIO**: for object storage.
- **Prometheus** for runtime monitoring and alerting
- **Kafka**: for streaming prediction requests to drift detection service
- **Drift**: for data drift and concept drift detection

## Before you begin

Before deploying the MLOps infrastructure, please perform the following steps:

1. Clone this repository:

  ```bash
    git clone https://github.com/KhaosResearch/mlops-infra.git
    cd mlops-infra
  ```

1. Run the following sed commands to replace placeholders in the repository with your specific cluster and MinIO/S3 IP addresses.

  ```bash
    # Replace your_kubernetes_cluster_ip with your Kubernetes cluster IP
    sed -i 's/<CLUSTER-IP>/your_kubernetes_cluster_ip/g' $(grep -rl '<CLUSTER-IP>' *)
  ```
  ```bash
    # Replace your_minio_s3_ip with your MinIO/S3 IP
    sed -i 's/<S3-IP>/your_minio_s3_ip/g' $(grep -rl '<S3-IP>' *)
  ```

3. Run the following sed commands to replace placeholders in the repository with your specific ports.

  ```bash
    # Replace your_prefect_api_port with your Prefect API port
    sed -i 's/<PREFECT-API-PORT>/your_prefect_api_port/g' $(grep -rl '<PREFECT-API-PORT>' *)
  ```
  ```bash
    # Replace your_mlflow_port with your mlflow port
    sed -i 's/<MLFLOW-PORT>/your_mlflow_port/g' $(grep -rl '<MLFLOW-PORT>' *)
  ```
  ```bash
    # Replace your_phometheus_port with your Prometheus port
    sed -i 's/<PROMETHEUS-PORT>/your_phometheus_port/g' $(grep -rl '<PROMETHEUS-PORT>' *)
  ```
  ```bash
    # Replace your_kafka_service_port with your kafka service port
    sed -i 's/<KAFKA-SERVICE-PORT>/your_kafka_service_port/g' $(grep -rl '<KAFKA-SERVICE-PORT>' *)
  ```
  ```bash
    # Replace your_kafka_controller_1_port with your first kafka controller port
    sed -i 's/<KAFKA-CONTROLLER-PORT-1>/your_kafka_controller_1_port/g' $(grep -rl '<KAFKA-CONTROLLER-PORT-1>' *)
  ```
  ```bash
    # Replace your_kafka_controller_2_port with your second kafka controller port
    sed -i 's/<KAFKA-CONTROLLER-PORT-2>/your_kafka_controller_2_port/g' $(grep -rl '<KAFKA-CONTROLLER-PORT-2>' *)
  ```
  ```bash
    # Replace your_kafka_controller_3_port with your third kafka controller port
    sed -i 's/<KAFKA-CONTROLLER-PORT-3>/your_kafka_controller_3_port/g' $(grep -rl '<KAFKA-CONTROLLER-PORT-3>' *)
  ```
  ```bash
    # Replace your_s3_port with your S3 port
    sed -i 's/<S3-PORT>/your_s3_port/g' $(grep -rl '<S3-PORT>' *)
  ```

## MLflow installation

Versions:

- Python 3.11.3
- PostgreSQL chart version 12.5.6
- Postgre version 15.3.0

- (Optional) if the clusted doesnt have a default PV:

  `helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/`  
  
  `helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --set nfs.server=<CLUSTER-IP> --set nfs.path=/mnt/nfs_share --version 4.0.18`  
  
  `kubectl patch storageclass nfs-client -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'`

- Install postgreSQL

  ```
  helm install postgresql-mlflow bitnami/postgresql -n mlops-mlflow \
  --set global.postgresql.auth.database=mlflow-tracking-server \
  --set global.postgresql.auth.postgresPassword=khaosdev \
  --version 12.5.6
  ```

- Deploy secret and configmap defining required variables

  `kubectl apply -f mlflow/configmap.yaml`
  
  `kubectl apply -f mlflow/secret.yaml`

- Deploy mlflow using defined variables, the mlflow image was already built and pushed to `ghcr.io`. `Dockerfile` is also in the folder anyways.

  `kubectl apply -f mlflow/deployment.yaml`

- Deploy service and nodeport, making mlflow UI accesible at `http://<CLUSTER-IP>:<MLFLOW-PORT>/`

  `kubectl apply -f mlflow/service.yaml`
  
  `kubectl apply -f mlflow/nodeport.yaml`

## Seldon Core installation

Versions:

- Python 3.11.3
- Seldon Core chart 1.16.0
- Seldon Core 1.16.0

- Download istio

  `curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.17.2 TARGET_ARCH=x86_64 sh -`

- Install istio

  `./istio-1.17.2/bin/istioctl install --set profile=demo -y`

- Create required gateway 

  `kubectl apply -f ./seldon/seldon-gateway.yaml`

- Install Seldon (using Istio)

  ```
  helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set istio.enabled=true \
    --namespace mlops-seldon \
    --version 1.16.0
    ```

- TODO deploy test model

## Prefect Server installation

[Helm chart repo](https://github.com/PrefectHQ/prefect-helm/tree/main)

Versions:

- Python 3.11.3
- Prefect chart 2023.04.13
- Prefect 2.10.4
- Prefect Kubernetes 0.2.4

### How to deploy server in K8s:

- Create namespace  
  
  `kubectl create namespace mlops-prefect`

- Add prefect helm repo  
  
  `helm repo add prefect https://prefecthq.github.io/prefect-helm`

- Search prefect helm repo  
  
  `helm search repo prefect`

- Install prefect server in created namespace using custom values    
  
  `helm install prefect-server prefect/prefect-server -n mlops-prefect -f prefect/values.yaml --version 2023.04.13`

### Configure a client to use the server

- Install prefect in the client  
  
  `pip install prefect==2.10.4 prefect-kubernetes==0.2.4`

- Create server profile and modify api url parameter  
  
  `prefect profile create server`  

  `prefect profile use 'server' `   

  `prefect config set PREFECT_API_URL="http://<CLUSTER-IP>:<PREFECT-API-PORT>/api"`

### Create useful blocks

- Execute the file `init_blocks.py`, which creates useful blocks (MinIO user and password has to be added first).  
  
  `python prefect/init_blocks.py`

- Create a work pool for sending flows that will be executed in Kubernetes
  
  `prefect work-pool create k8s-pool`

### Create and run a deployment

- Create a deployment for the testing flow using the K8s infrastructure (should be similar to the one in github `test_flow_deployment.yaml`). To let prefect uploading deployment files to the storage block (MinIO), environment variable `FSSPEC_S3_ENDPOINT_URL` has to be set. 
  
  `cd prefect/test-flow`

  `export FSSPEC_S3_ENDPOINT_URL=http://<S3-IP>:<S3-PORT>`

  `prefect deployment build -n test-flow-deployment-k8s -p k8s-pool -ib kubernetes-job/k8s-infra -sb s3/khaos-minio -o test_flow_deployment.yaml test_flow.py:flow`  

  `prefect deployment apply test_flow_deployment.yaml`

- Create a quick run of the deployment using the UI and check if the flow is succesfully executed (an agent have to be created first)

  `prefect agent start --pool k8s-pool --work-queue default`

## Prometheus operator installation

Versions:

- Python 3.11.3
- Prometheus operator chart version 8.3.2
- Postgre version 15.3.0

- Create a namespace

  `kubectl create namespace mlops-prometheus`  

- Install Prometheus operator in created namespace using custom values 
    
  `helm install prometheus bitnami/kube-prometheus --version 8.3.2 --namespace mlops-prometheus -f prometheus/values.yaml` 

## Kafka installation

Versions:

- Python 3.11.3
- Prometheus operator chart version 25.1.12

- Create a namespace

  `kubectl create namespace mlops-kafka` 

- Install Kafka in created namespace using custom values

  `helm install kafka -n mlops-kafka oci://registry-1.docker.io/bitnamicharts/kafka -f kafka/values.yaml --version 25.1.12`