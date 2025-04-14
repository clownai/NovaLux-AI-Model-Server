#!/bin/bash

# Test script for NovaLux AI Model Server
# This script tests the functionality of the AI model server components

set -e

echo "===== NovaLux AI Model Server Test Script ====="
echo "Starting tests at $(date)"
echo

# Define color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print success message
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
error() {
  echo -e "${RED}✗ $1${NC}"
  exit 1
}

# Function to print warning message
warning() {
  echo -e "${YELLOW}! $1${NC}"
}

# Function to test Kubernetes namespace configuration
test_namespace_configuration() {
  echo "Testing Kubernetes namespace configuration..."
  
  # Check if namespace configuration file exists
  if [ ! -f "kubernetes/namespace-config.yaml" ]; then
    error "Namespace configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/namespace-config.yaml > /dev/null 2>&1 || error "Invalid YAML in namespace configuration"
  
  # Check for required resources in the namespace configuration
  grep -q "kind: Namespace" kubernetes/namespace-config.yaml || error "Namespace definition not found"
  grep -q "kind: ResourceQuota" kubernetes/namespace-config.yaml || error "ResourceQuota not found"
  grep -q "kind: NetworkPolicy" kubernetes/namespace-config.yaml || error "NetworkPolicy not found"
  grep -q "kind: ConfigMap" kubernetes/namespace-config.yaml || error "ConfigMap not found"
  
  success "Namespace configuration is valid"
}

# Function to test model server deployment
test_model_server_deployment() {
  echo "Testing model server deployment configuration..."
  
  # Check if deployment configuration file exists
  if [ ! -f "kubernetes/model-server-deployment.yaml" ]; then
    error "Model server deployment configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/model-server-deployment.yaml > /dev/null 2>&1 || error "Invalid YAML in model server deployment"
  
  # Check for required resources in the deployment configuration
  grep -q "kind: Deployment" kubernetes/model-server-deployment.yaml || error "Deployment definition not found"
  grep -q "kind: Service" kubernetes/model-server-deployment.yaml || error "Service definition not found"
  grep -q "kind: PersistentVolumeClaim" kubernetes/model-server-deployment.yaml || error "PersistentVolumeClaim not found"
  grep -q "kind: HorizontalPodAutoscaler" kubernetes/model-server-deployment.yaml || error "HorizontalPodAutoscaler not found"
  
  # Check for required container configuration
  grep -q "containerPort: 8000" kubernetes/model-server-deployment.yaml || error "HTTP port not configured"
  grep -q "containerPort: 8001" kubernetes/model-server-deployment.yaml || error "gRPC port not configured"
  grep -q "containerPort: 9090" kubernetes/model-server-deployment.yaml || error "Metrics port not configured"
  
  # Check for resource requests and limits
  grep -q "requests:" kubernetes/model-server-deployment.yaml || error "Resource requests not configured"
  grep -q "limits:" kubernetes/model-server-deployment.yaml || error "Resource limits not configured"
  
  # Check for health probes
  grep -q "livenessProbe:" kubernetes/model-server-deployment.yaml || error "Liveness probe not configured"
  grep -q "readinessProbe:" kubernetes/model-server-deployment.yaml || error "Readiness probe not configured"
  
  success "Model server deployment configuration is valid"
}

# Function to test model registry and storage
test_model_registry() {
  echo "Testing model registry and storage configuration..."
  
  # Check if model registry configuration file exists
  if [ ! -f "kubernetes/model-registry.yaml" ]; then
    error "Model registry configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/model-registry.yaml > /dev/null 2>&1 || error "Invalid YAML in model registry configuration"
  
  # Check for required resources in the registry configuration
  grep -q "name: novalux-model-registry" kubernetes/model-registry.yaml || error "Model registry deployment not found"
  grep -q "name: model-registry-db" kubernetes/model-registry.yaml || error "Database deployment not found"
  grep -q "name: novalux-model-registry-storage" kubernetes/model-registry.yaml || error "Storage PVC not found"
  grep -q "name: model-registry-backup" kubernetes/model-registry.yaml || error "Backup cronjob not found"
  
  # Check for required container configuration
  grep -q "containerPort: 8080" kubernetes/model-registry.yaml || error "HTTP port not configured for model registry"
  grep -q "containerPort: 5432" kubernetes/model-registry.yaml || error "PostgreSQL port not configured"
  
  # Check for persistent storage
  grep -q "persistentVolumeClaim:" kubernetes/model-registry.yaml || error "Persistent volume claim not configured"
  
  success "Model registry and storage configuration is valid"
}

# Function to test inference API service
test_inference_api() {
  echo "Testing inference API service configuration..."
  
  # Check if inference API configuration file exists
  if [ ! -f "kubernetes/inference-api.yaml" ]; then
    error "Inference API configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/inference-api.yaml > /dev/null 2>&1 || error "Invalid YAML in inference API configuration"
  
  # Check for required resources in the API configuration
  grep -q "name: novalux-inference-api" kubernetes/inference-api.yaml || error "Inference API deployment not found"
  grep -q "kind: Service" kubernetes/inference-api.yaml || error "Service definition not found"
  grep -q "kind: ConfigMap" kubernetes/inference-api.yaml || error "ConfigMap not found"
  grep -q "kind: NetworkPolicy" kubernetes/inference-api.yaml || error "NetworkPolicy not found"
  grep -q "kind: HorizontalPodAutoscaler" kubernetes/inference-api.yaml || error "HorizontalPodAutoscaler not found"
  
  # Check for required container configuration
  grep -q "containerPort: 8080" kubernetes/inference-api.yaml || error "HTTP port not configured"
  grep -q "containerPort: 8081" kubernetes/inference-api.yaml || error "gRPC port not configured"
  grep -q "containerPort: 9090" kubernetes/inference-api.yaml || error "Metrics port not configured"
  
  # Check for API configuration
  grep -q "api-config.yaml:" kubernetes/inference-api.yaml || error "API configuration not found"
  grep -q "predict-schema.json:" kubernetes/inference-api.yaml || error "Prediction schema not found"
  grep -q "batch-predict-schema.json:" kubernetes/inference-api.yaml || error "Batch prediction schema not found"
  
  # Check for health probes
  grep -q "livenessProbe:" kubernetes/inference-api.yaml || error "Liveness probe not configured"
  grep -q "readinessProbe:" kubernetes/inference-api.yaml || error "Readiness probe not configured"
  
  success "Inference API service configuration is valid"
}

# Function to test training infrastructure
test_training_infrastructure() {
  echo "Testing training infrastructure configuration..."
  
  # Check if training infrastructure configuration file exists
  if [ ! -f "kubernetes/training-infrastructure.yaml" ]; then
    error "Training infrastructure configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/training-infrastructure.yaml > /dev/null 2>&1 || error "Invalid YAML in training infrastructure configuration"
  
  # Check for required resources in the training configuration
  grep -q "name: novalux-training-orchestrator" kubernetes/training-infrastructure.yaml || error "Training orchestrator deployment not found"
  grep -q "name: novalux-feature-store" kubernetes/training-infrastructure.yaml || error "Feature store deployment not found"
  grep -q "name: novalux-experiment-tracker" kubernetes/training-infrastructure.yaml || error "Experiment tracker deployment not found"
  grep -q "name: novalux-training-scheduler" kubernetes/training-infrastructure.yaml || error "Training scheduler cronjob not found"
  
  # Check for required container configuration
  grep -q "containerPort: 8080" kubernetes/training-infrastructure.yaml || error "HTTP port not configured for training orchestrator"
  
  # Check for training configuration
  grep -q "training-orchestrator.yaml:" kubernetes/training-infrastructure.yaml || error "Training orchestrator configuration not found"
  grep -q "player-behavior-analyzer" kubernetes/training-infrastructure.yaml || error "Player behavior analyzer model not found"
  grep -q "game-balance-optimizer" kubernetes/training-infrastructure.yaml || error "Game balance optimizer model not found"
  grep -q "content-recommendation-engine" kubernetes/training-infrastructure.yaml || error "Content recommendation engine model not found"
  grep -q "responsible-gaming-monitor" kubernetes/training-infrastructure.yaml || error "Responsible gaming monitor model not found"
  
  # Check for persistent storage
  grep -q "persistentVolumeClaim:" kubernetes/training-infrastructure.yaml || error "Persistent volume claim not configured"
  
  success "Training infrastructure configuration is valid"
}

# Function to test monitoring and logging
test_monitoring_logging() {
  echo "Testing monitoring and logging configuration..."
  
  # Check if monitoring and logging configuration file exists
  if [ ! -f "kubernetes/monitoring-logging.yaml" ]; then
    error "Monitoring and logging configuration file not found"
  fi
  
  # Validate YAML syntax
  kubectl apply --dry-run=client -f kubernetes/monitoring-logging.yaml > /dev/null 2>&1 || error "Invalid YAML in monitoring and logging configuration"
  
  # Check for required resources in the monitoring configuration
  grep -q "name: novalux-monitoring" kubernetes/monitoring-logging.yaml || error "Monitoring deployment not found"
  grep -q "name: novalux-logging" kubernetes/monitoring-logging.yaml || error "Logging deployment not found"
  grep -q "name: novalux-prometheus-config" kubernetes/monitoring-logging.yaml || error "Prometheus configuration not found"
  grep -q "name: novalux-alertmanager-config" kubernetes/monitoring-logging.yaml || error "Alertmanager configuration not found"
  grep -q "name: novalux-grafana-provisioning" kubernetes/monitoring-logging.yaml || error "Grafana provisioning not found"
  grep -q "name: novalux-fluentd-config" kubernetes/monitoring-logging.yaml || error "Fluentd configuration not found"
  
  # Check for required container configuration
  grep -q "name: prometheus" kubernetes/monitoring-logging.yaml || error "Prometheus container not found"
  grep -q "name: grafana" kubernetes/monitoring-logging.yaml || error "Grafana container not found"
  grep -q "name: alertmanager" kubernetes/monitoring-logging.yaml || error "Alertmanager container not found"
  grep -q "name: fluentd" kubernetes/monitoring-logging.yaml || error "Fluentd container not found"
  
  # Check for persistent storage
  grep -q "persistentVolumeClaim:" kubernetes/monitoring-logging.yaml || error "Persistent volume claim not configured"
  
  # Check for monitoring configuration
  grep -q "prometheus.yml:" kubernetes/monitoring-logging.yaml || error "Prometheus configuration not found"
  grep -q "alertmanager.yml:" kubernetes/monitoring-logging.yaml || error "Alertmanager configuration not found"
  grep -q "fluent.conf:" kubernetes/monitoring-logging.yaml || error "Fluentd configuration not found"
  
  success "Monitoring and logging configuration is valid"
}

# Function to test integration between components
test_integration() {
  echo "Testing integration between components..."
  
  # Check for model server integration with Kafka
  grep -q "KAFKA_BOOTSTRAP_SERVERS" kubernetes/model-server-deployment.yaml || warning "Model server may not be integrated with Kafka"
  
  # Check for model server integration with Elasticsearch
  grep -q "ELASTICSEARCH_HOSTS" kubernetes/model-server-deployment.yaml || warning "Model server may not be integrated with Elasticsearch"
  
  # Check for inference API integration with model server
  grep -q "MODEL_SERVER_URL" kubernetes/inference-api.yaml || error "Inference API not integrated with model server"
  
  # Check for inference API integration with model registry
  grep -q "MODEL_REGISTRY_URL" kubernetes/inference-api.yaml || error "Inference API not integrated with model registry"
  
  # Check for training orchestrator integration with model registry
  grep -q "MODEL_REGISTRY_URL" kubernetes/training-infrastructure.yaml || error "Training orchestrator not integrated with model registry"
  
  # Check for training orchestrator integration with Kafka
  grep -q "KAFKA_BOOTSTRAP_SERVERS" kubernetes/training-infrastructure.yaml || warning "Training orchestrator may not be integrated with Kafka"
  
  # Check for monitoring integration with model server
  grep -q "job_name: 'novalux-model-server'" kubernetes/monitoring-logging.yaml || warning "Monitoring may not be integrated with model server"
  
  # Check for logging integration with model server
  grep -q "novalux-model-server-logs" kubernetes/monitoring-logging.yaml || warning "Logging may not be integrated with model server"
  
  success "Component integration is valid"
}

# Function to test overall system configuration
test_system_configuration() {
  echo "Testing overall system configuration..."
  
  # Check if all required configuration files exist
  required_files=(
    "kubernetes/namespace-config.yaml"
    "kubernetes/model-server-deployment.yaml"
    "kubernetes/model-registry.yaml"
    "kubernetes/inference-api.yaml"
    "kubernetes/training-infrastructure.yaml"
    "kubernetes/monitoring-logging.yaml"
  )
  
  for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
      error "Required configuration file not found: $file"
    fi
  done
  
  # Check for consistent namespace usage
  for file in kubernetes/*.yaml; do
    if ! grep -q "namespace: novalux-ai" "$file"; then
      warning "File $file may not use the correct namespace"
    fi
  done
  
  # Check for consistent labeling
  for file in kubernetes/*.yaml; do
    if ! grep -q "component: ai-processing" "$file"; then
      warning "File $file may not use consistent labeling"
    fi
  done
  
  success "Overall system configuration is valid"
}

# Run all tests
echo "Running tests in NovaLux-AI-Model-Server directory..."
cd /home/ubuntu/NovaLux-AI-Model-Server || error "NovaLux-AI-Model-Server directory not found"

echo
test_namespace_configuration
echo
test_model_server_deployment
echo
test_model_registry
echo
test_inference_api
echo
test_training_infrastructure
echo
test_monitoring_logging
echo
test_integration
echo
test_system_configuration

echo
echo -e "${GREEN}===== All tests passed successfully! =====${NC}"
echo "NovaLux AI Model Server implementation is valid and ready for deployment."
echo "Completed tests at $(date)"
