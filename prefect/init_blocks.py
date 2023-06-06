from prefect.blocks.kubernetes import KubernetesClusterConfig
from prefect.filesystems import S3
from prefect.infrastructure.kubernetes import KubernetesJob

minio_creds = S3(
    bucket_path="***REMOVED***/prefect",
    aws_access_key_id="USERNAME",
    aws_secret_access_key="PASSWORD"
)

k8s_config = KubernetesClusterConfig.from_file(
    path="~/.kube/config",
    context_name="kubernetes-admin@kubernetes"
)

infra_k8s = KubernetesJob(
    env={
        'PREFECT_API_URL': 'http://<CLUSTER-IP>:<PREFECT-API-PORT>/api',
        'EXTRA_PIP_PACKAGES': 's3fs==2023.4.0',
        'FSSPEC_S3_ENDPOINT_URL': 'http://<S3-IP>:<S3-PORT>'
    },
    image="prefecthq/prefect:2.10.4-python3.11",
    namespace="mlops-prefect",
    image_pull_policy="IfNotPresent",
    cluster_config=k8s_config,
    job=KubernetesJob.base_job_manifest(),
    finished_job_ttl=60
)

k8s_config.save("k8s-config", overwrite=True)
print("KubernetesClusterConfig/k8s-config deployed")
minio_creds.save("khaos-minio", overwrite=True)
print("S3/khaos-minio deployed")
infra_k8s.save("k8s-infra", overwrite=True)
print("KubernetesJob/k8s-infra deployed")
