import argparse
import json
import os

import mlflow
import numpy as np
import pandas as pd
from alibi_detect.cd import MMDDriftOnline
from confluent_kafka import Consumer, KafkaException
from prometheus_client import start_http_server, Gauge

DRIFT_METRIC = Gauge('drift_value', 'drift value in model predictions')

class DriftDetector:

    def __init__(self, model_name, model_version, algorithm, file_path="files"):
        self.model_name = model_name
        self.model_version = model_version
        self.algorithm = algorithm
        self.file_path = file_path
        self.detector = self._train_drift_detector()

    def _train_drift_detector(self):
        model_uri = f"models:/{self.model_name}/{self.model_version}"
        download_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri, dst_path=self.file_path)
        training_data_file = os.path.join(download_path, "artifacts", "testing_dataset.csv")
        training_data = pd.read_csv(training_data_file).values[:300, :-1].astype(np.float32)
        if self.algorithm == 'online-MMD':
            detector = MMDDriftOnline(training_data, 100, 100, backend="pytorch")
        else:
            raise NotImplementedError(f"Algorithm {self.algorithm} not implemented")
        return detector

    def predict(self, X):
        preds = self.detector.predict(X, return_test_stat=True)
        return preds


def parse_arguments():
    parser = argparse.ArgumentParser(description='Drift Detector Script')
    parser.add_argument('--model-name', required=True, help='Name of the model')
    parser.add_argument('--model-version', required=True, help='Version of the model')
    parser.add_argument('--algorithm', required=True, help='Drift detection algorithm')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])

    conf = {
        'bootstrap.servers': os.environ['KAFKA_BOOTSTRAP_SERVERS'], 
        'group.id': "drift-detector",
        'auto.offset.reset': 'latest',
        'security.protocol': 'PLAINTEXT',
    }

    drift_detector = DriftDetector(model_name=args.model_name, model_version=args.model_version, algorithm=args.algorithm)
    
    start_http_server(8000)

    consumer = Consumer(conf)

    topics = [drift_detector.model_name]
    consumer.subscribe(topics)

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            input_data = np.array(dict(json.loads(msg.value().decode('utf-8')))['X'][0], dtype=np.float32)

            preds = drift_detector.predict(input_data)
            drift_value = preds['data']['test_stat']
            DRIFT_METRIC.set(drift_value)
            print(f"{DRIFT_METRIC}: {drift_value}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

