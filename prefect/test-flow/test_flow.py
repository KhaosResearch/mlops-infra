from prefect import flow, task
import os

os.environ["PREFECT_API_URL"] = "http://192.168.219.33:<PREFECT-API-PORT>/api"


@task
def my_task():
    print("Hello, I'm a task")

@flow
def my_flow():
    my_task()

