FROM python:3.11.3

LABEL org.opencontainers.image.source=https://github.com/KhaosResearch/mlops-infra/
LABEL org.opencontainers.image.description="Drift detector deployment image"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /home
COPY requirements.txt /home

RUN pip install -r requirements.txt

COPY drift_detector.py /home

EXPOSE 8000

ENTRYPOINT ["python", "drift_detector.py"]
CMD ["--model-name", "test-model", "--model-version", "latest", "--algorithm", "test-algorithm"]
