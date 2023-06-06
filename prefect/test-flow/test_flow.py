from prefect import flow, task

@task
def my_task():
    print("Hello, I'm a task")

@flow
def flow():
    my_task()

