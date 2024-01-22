#!/bin/bash

CONFIG_FILE=config.conf

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found. Please create the configuration file and try again."
    exit 1
fi

# Load configuration from config.conf
source $CONFIG_FILE

# Replace placeholders with user-specific values
sed -i "s/<CLUSTER-IP>/$CLUSTER_IP/g" $(grep -rl '<CLUSTER-IP>' *)
sed -i "s/<S3-IP>/$S3_IP/g" $(grep -rl '<S3-IP>' *)
sed -i "s/<PREFECT-API-PORT>/$PREFECT_API_PORT/g" $(grep -rl '<PREFECT-API-PORT>' *)
sed -i "s/<MLFLOW-PORT>/$MLFLOW_PORT/g" $(grep -rl '<MLFLOW-PORT>' *)
sed -i "s/<PROMETHEUS-PORT>/$PROMETHEUS_PORT/g" $(grep -rl '<PROMETHEUS-PORT>' *)
sed -i "s/<KAFKA-SERVICE-PORT>/$KAFKA_SERVICE_PORT/g" $(grep -rl '<KAFKA-SERVICE-PORT>' *)
sed -i "s/<KAFKA-CONTROLLER-PORT-1>/$KAFKA_CONTROLLER_PORT_1/g" $(grep -rl '<KAFKA-CONTROLLER-PORT-1>' *)
sed -i "s/<KAFKA-CONTROLLER-PORT-2>/$KAFKA_CONTROLLER_PORT_2/g" $(grep -rl '<KAFKA-CONTROLLER-PORT-2>' *)
sed -i "s/<KAFKA-CONTROLLER-PORT-3>/$KAFKA_CONTROLLER_PORT_3/g" $(grep -rl '<KAFKA-CONTROLLER-PORT-3>' *)
sed -i "s/<S3-PORT>/$S3_PORT/g" $(grep -rl '<S3-PORT>' *)

echo "Config variables setup completed. Proceed with deployment steps of each service as outlined in the README."
