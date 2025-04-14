# NovaLux AI Model Server Documentation

## Overview

This document provides comprehensive documentation for the NovaLux AI Model Server implementation in the `novalux-ai` namespace. The AI Model Server is a critical component of the NovaLux AI Casino platform's Forever Growth Loop architecture, providing the AI capabilities needed for player behavior analysis, game balance optimization, content recommendation, and responsible gaming monitoring.

## Architecture

The NovaLux AI Model Server follows a microservices architecture deployed on Kubernetes in the `novalux-ai` namespace. The system consists of the following key components:

1. **Model Serving Layer**: Handles model inference requests in real-time and batch modes
2. **Model Registry**: Manages model versions, artifacts, and metadata
3. **Inference API**: Provides HTTP and gRPC endpoints for model inference
4. **Training Infrastructure**: Orchestrates model training, evaluation, and deployment
5. **Monitoring & Observability**: Tracks system health, performance, and model metrics

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       NovaLux AI Model Server                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐           ┌─────────────────┐                  │
│  │                 │           │                 │                  │
│  │  Inference API  │◄─────────►│  Model Server   │                  │
│  │  (REST/gRPC)    │           │                 │                  │
│  │                 │           │                 │                  │
│  └────────┬────────┘           └────────┬────────┘                  │
│           │                             │                           │
│           │                             │                           │
│           ▼                             ▼                           │
│  ┌─────────────────┐           ┌─────────────────┐                  │
│  │                 │           │                 │                  │
│  │ Kafka           │◄─────────►│   Model         │                  │
│  │ Integration     │           │   Registry      │                  │
│  │                 │           │                 │                  │
│  └────────┬────────┘           └─────────────────┘                  │
│           │                             ▲                           │
│           │                             │                           │
│           ▼                             │                           │
│  ┌─────────────────┐           ┌─────────────────┐                  │
│  │                 │           │                 │                  │
│  │ Training        │◄─────────►│   Feature       │                  │
│  │ Orchestrator    │           │   Store         │                  │
│  │                 │           │                 │                  │
│  └────────┬────────┘           └─────────────────┘                  │
│           │                                                         │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                     Monitoring & Observability                   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Kubernetes Namespace Configuration

The `novalux-ai` namespace is configured with resource quotas, network policies, and RBAC permissions to ensure secure and efficient operation of the AI Model Server.

**Key Features:**
- Resource quotas for CPU, memory, and GPU resources
- Network policies for secure communication
- Service accounts with appropriate permissions
- ConfigMaps for component configuration

**Configuration File:** `kubernetes/namespace-config.yaml`

### 2. Model Server Deployment

The Model Server is the core component responsible for serving AI models and processing inference requests. It is deployed as a scalable Kubernetes deployment with appropriate resource allocations and health checks.

**Key Features:**
- Horizontal scaling based on CPU and memory utilization
- Support for multiple model types (TensorFlow, ONNX, PyTorch)
- Real-time and batch inference capabilities
- Model caching for improved performance
- Integration with Kafka and Elasticsearch

**Configuration File:** `kubernetes/model-server-deployment.yaml`

### 3. Model Registry

The Model Registry manages model versions, artifacts, and metadata. It provides a central repository for storing and retrieving models, ensuring consistent versioning and deployment.

**Key Features:**
- Model versioning and aliasing
- Metadata storage in PostgreSQL database
- Artifact storage in persistent volumes
- Backup and recovery capabilities
- Integration with the Training Orchestrator

**Configuration File:** `kubernetes/model-registry.yaml`

### 4. Inference API

The Inference API provides HTTP and gRPC endpoints for model inference. It handles authentication, rate limiting, request validation, and routing to the appropriate model server.

**Key Features:**
- REST and gRPC interfaces
- Authentication and authorization
- Rate limiting and request validation
- Model version selection
- Request and response logging
- Integration with Kafka for event-driven inference

**Configuration File:** `kubernetes/inference-api.yaml`

### 5. Training Infrastructure

The Training Infrastructure orchestrates model training, evaluation, and deployment. It includes a training orchestrator, feature store, experiment tracker, and training scheduler.

**Key Features:**
- Scheduled and on-demand training
- Feature management and versioning
- Experiment tracking and model evaluation
- Automated model deployment
- Integration with the Model Registry

**Configuration File:** `kubernetes/training-infrastructure.yaml`

### 6. Monitoring and Logging

The Monitoring and Logging components provide observability into the AI Model Server's performance and health. They include Prometheus for metrics collection, Grafana for visualization, Alertmanager for alerts, and Fluentd for log collection.

**Key Features:**
- Real-time metrics collection and visualization
- Alerting based on performance thresholds
- Log aggregation and analysis
- Custom dashboards for model performance
- Integration with Elasticsearch for log storage

**Configuration File:** `kubernetes/monitoring-logging.yaml`

## Deployment

### Prerequisites

Before deploying the NovaLux AI Model Server, ensure the following prerequisites are met:

1. Kubernetes cluster with version 1.19 or higher
2. Kafka cluster deployed in the `novalux-data` namespace
3. Elasticsearch cluster deployed in the `novalux-data` namespace
4. Storage class for persistent volumes
5. NVIDIA device plugin for GPU support (if using GPUs)

### Deployment Steps

1. Create the `novalux-ai` namespace and apply resource quotas:
   ```bash
   kubectl apply -f kubernetes/namespace-config.yaml
   ```

2. Deploy the Model Registry:
   ```bash
   kubectl apply -f kubernetes/model-registry.yaml
   ```

3. Deploy the Model Server:
   ```bash
   kubectl apply -f kubernetes/model-server-deployment.yaml
   ```

4. Deploy the Inference API:
   ```bash
   kubectl apply -f kubernetes/inference-api.yaml
   ```

5. Deploy the Training Infrastructure:
   ```bash
   kubectl apply -f kubernetes/training-infrastructure.yaml
   ```

6. Deploy the Monitoring and Logging components:
   ```bash
   kubectl apply -f kubernetes/monitoring-logging.yaml
   ```

### Verification

After deployment, verify that all components are running correctly:

1. Check the status of all pods in the `novalux-ai` namespace:
   ```bash
   kubectl get pods -n novalux-ai
   ```

2. Verify that the services are accessible:
   ```bash
   kubectl get svc -n novalux-ai
   ```

3. Run the test script to validate the deployment:
   ```bash
   ./test.sh
   ```

## Usage

### Inference API

The Inference API provides the following endpoints for model inference:

1. **List Models**
   - Endpoint: `/v1/models`
   - Method: GET
   - Description: Lists all available models

2. **List Model Versions**
   - Endpoint: `/v1/models/{model_name}/versions`
   - Method: GET
   - Description: Lists all available versions for a specific model

3. **Predict (Latest Version)**
   - Endpoint: `/v1/models/{model_name}/predict`
   - Method: POST
   - Description: Makes a prediction using the latest version of the specified model
   - Request Body: JSON object with `instances` array and optional `parameters`

4. **Predict (Specific Version)**
   - Endpoint: `/v1/models/{model_name}/versions/{version}/predict`
   - Method: POST
   - Description: Makes a prediction using a specific version of the specified model
   - Request Body: JSON object with `instances` array and optional `parameters`

5. **Batch Predict (Latest Version)**
   - Endpoint: `/v1/models/{model_name}/batch-predict`
   - Method: POST
   - Description: Makes batch predictions using the latest version of the specified model
   - Request Body: JSON object with `instances` array and optional `parameters`

6. **Batch Predict (Specific Version)**
   - Endpoint: `/v1/models/{model_name}/versions/{version}/batch-predict`
   - Method: POST
   - Description: Makes batch predictions using a specific version of the specified model
   - Request Body: JSON object with `instances` array and optional `parameters`

### Model Registry API

The Model Registry API provides the following endpoints for model management:

1. **List Models**
   - Endpoint: `/models`
   - Method: GET
   - Description: Lists all registered models

2. **Get Model**
   - Endpoint: `/models/{model_name}`
   - Method: GET
   - Description: Gets details for a specific model

3. **Create Model**
   - Endpoint: `/models`
   - Method: POST
   - Description: Creates a new model
   - Request Body: JSON object with model metadata

4. **Upload Model Version**
   - Endpoint: `/models/{model_name}/versions`
   - Method: POST
   - Description: Uploads a new version of a model
   - Request Body: Multipart form with model artifacts and metadata

5. **Get Model Version**
   - Endpoint: `/models/{model_name}/versions/{version}`
   - Method: GET
   - Description: Gets details for a specific model version

6. **Set Default Version**
   - Endpoint: `/models/{model_name}/versions/{version}/default`
   - Method: POST
   - Description: Sets a specific version as the default for a model

### Training Orchestrator API

The Training Orchestrator API provides the following endpoints for training management:

1. **List Training Jobs**
   - Endpoint: `/jobs`
   - Method: GET
   - Description: Lists all training jobs

2. **Get Training Job**
   - Endpoint: `/jobs/{job_id}`
   - Method: GET
   - Description: Gets details for a specific training job

3. **Create Training Job**
   - Endpoint: `/jobs`
   - Method: POST
   - Description: Creates a new training job
   - Request Body: JSON object with training job configuration

4. **Cancel Training Job**
   - Endpoint: `/jobs/{job_id}/cancel`
   - Method: POST
   - Description: Cancels a running training job

5. **Get Training Job Logs**
   - Endpoint: `/jobs/{job_id}/logs`
   - Method: GET
   - Description: Gets logs for a specific training job

## Models

The NovaLux AI Model Server includes the following AI models:

### 1. Player Behavior Analyzer

**Description:** Analyzes player behavior to identify patterns, preferences, and risk profiles.

**Use Cases:**
- Player clustering and segmentation
- Risk tolerance assessment
- Engagement pattern recognition
- Churn prediction

**Training Schedule:** Daily at 2 AM

**Evaluation Metrics:**
- Accuracy: 0.85 (threshold)
- F1-Score: 0.80 (threshold)
- Precision: 0.75 (threshold)
- Recall: 0.75 (threshold)

### 2. Game Balance Optimizer

**Description:** Optimizes game parameters for balanced gameplay and player satisfaction.

**Use Cases:**
- Difficulty curve optimization
- Reward frequency tuning
- Progression speed adjustment
- Economic balancing for faction competition

**Training Schedule:** Daily at 3 AM

**Evaluation Metrics:**
- Mean Squared Error: 0.1 (threshold)
- R-Squared: 0.7 (threshold)

### 3. Content Recommendation Engine

**Description:** Recommends personalized content based on player preferences and behavior.

**Use Cases:**
- Personalized game recommendations
- Content affinity prediction
- Next-best-action prediction

**Training Schedule:** Daily at 4 AM

**Evaluation Metrics:**
- NDCG@10: 0.65 (threshold)
- Precision@5: 0.7 (threshold)
- Recall@10: 0.6 (threshold)

### 4. Responsible Gaming Monitor

**Description:** Monitors player behavior for signs of problem gambling and suggests interventions.

**Use Cases:**
- Problem gambling detection
- Fatigue detection
- Mood-aware limit suggestion
- Intervention effectiveness prediction

**Training Schedule:** Daily at 1 AM

**Evaluation Metrics:**
- AUC-ROC: 0.85 (threshold)
- Precision: 0.8 (threshold)
- Recall: 0.75 (threshold)

## Monitoring and Alerting

### Metrics

The NovaLux AI Model Server collects the following metrics:

1. **Model Server Metrics:**
   - Request rate by model and version
   - Request latency (p50, p95, p99)
   - Error rate by model and version
   - Model loading time
   - Cache hit rate
   - Memory usage
   - CPU usage
   - GPU usage (if applicable)

2. **Inference API Metrics:**
   - Request rate by endpoint
   - Request latency (p50, p95, p99)
   - Error rate by endpoint
   - Authentication failures
   - Rate limiting rejections

3. **Training Metrics:**
   - Training job duration
   - Training job success rate
   - Model evaluation metrics
   - Resource utilization during training

### Dashboards

The following Grafana dashboards are available:

1. **Model Server Dashboard:**
   - Request rate by model
   - Latency by model
   - Error rate by model
   - Resource utilization

2. **Inference API Dashboard:**
   - Request rate by endpoint
   - Latency by endpoint
   - Error rate by endpoint
   - Authentication and rate limiting metrics

3. **Training Dashboard:**
   - Training job status
   - Training job duration
   - Model evaluation metrics
   - Resource utilization during training

### Alerts

The following alerts are configured:

1. **Model Server Alerts:**
   - High error rate (>5% for 5 minutes)
   - High latency (p99 >500ms for 5 minutes)
   - High memory usage (>90% for 5 minutes)
   - High CPU usage (>90% for 5 minutes)
   - Model load failure

2. **Inference API Alerts:**
   - High error rate (>5% for 5 minutes)
   - High latency (p99 >500ms for 5 minutes)
   - Authentication failure spike
   - Rate limiting rejection spike

3. **Training Alerts:**
   - Training job failure
   - Training job duration exceeding threshold
   - Model evaluation metrics below threshold

## Logging

The NovaLux AI Model Server uses Fluentd to collect logs from all components and forward them to Elasticsearch. The following log indices are created:

1. **Model Server Logs:**
   - Index: `novalux-model-server-logs`
   - Content: Model loading, inference requests, errors

2. **Inference API Logs:**
   - Index: `novalux-inference-api-logs`
   - Content: API requests, authentication, rate limiting

3. **Model Registry Logs:**
   - Index: `novalux-model-registry-logs`
   - Content: Model registration, version management

4. **Training Orchestrator Logs:**
   - Index: `novalux-training-orchestrator-logs`
   - Content: Training job management, scheduling

## Security

### Authentication and Authorization

The NovaLux AI Model Server uses token-based authentication for API access. Tokens are validated against the Adaptive Core Engine's authentication service.

RBAC is implemented at the Kubernetes level to control access to resources within the `novalux-ai` namespace.

### Network Security

Network policies are configured to restrict pod-to-pod communication within the `novalux-ai` namespace and between namespaces.

Only the Inference API is exposed to other namespaces, with specific ingress rules for the `novalux-system`, `novalux-data`, and `novalux-games` namespaces.

### Data Protection

Sensitive data is encrypted at rest using Kubernetes secrets and encrypted persistent volumes.

Data in transit is protected using TLS for all service-to-service communication.

## Integration with Other Components

### Integration with Adaptive Core Engine

The AI Model Server integrates with the Adaptive Core Engine in the `novalux-system` namespace through:

1. **API Calls:**
   - The Adaptive Core Engine calls the Inference API for model predictions
   - The Inference API validates authentication tokens with the Adaptive Core Engine

2. **Kafka Topics:**
   - The Adaptive Core Engine publishes events to the `model-inference-requests` topic
   - The AI Model Server publishes inference results to the `model-inference-results` topic

### Integration with Data Pipeline

The AI Model Server integrates with the Data Pipeline in the `novalux-data` namespace through:

1. **Kafka Integration:**
   - Consumes events from Kafka topics for processing
   - Publishes inference results back to Kafka topics

2. **Elasticsearch Integration:**
   - Stores model outputs and metrics in Elasticsearch
   - Retrieves historical data for model training

### Integration with Game Engines

The AI Model Server integrates with the Game Engines in the `novalux-games` namespace through:

1. **API Calls:**
   - Game Engines call the Inference API for real-time predictions
   - The Inference API provides game balance parameters and content recommendations

2. **Kafka Topics:**
   - Game Engines publish game events to Kafka topics
   - The AI Model Server processes these events for model training and inference

## Testing

The NovaLux AI Model Server includes a comprehensive test script (`test.sh`) that validates all aspects of the implementation:

1. **Namespace Configuration Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies resource quotas and network policies

2. **Model Server Deployment Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies container configuration, ports, and health probes

3. **Model Registry Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies database and storage configuration

4. **Inference API Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies API configuration and schemas

5. **Training Infrastructure Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies training configuration and scheduling

6. **Monitoring and Logging Testing:**
   - Validates YAML syntax
   - Checks for required resources
   - Verifies monitoring configuration and alerts

7. **Integration Testing:**
   - Verifies integration between components
   - Checks for required environment variables
   - Validates communication paths

## Future Enhancements

The following enhancements are planned for future iterations of the NovaLux AI Model Server:

1. **Advanced Model Serving:**
   - GPU optimization for inference
   - Multi-model ensembles
   - Online learning capabilities

2. **Enhanced Training Infrastructure:**
   - Distributed training support
   - Hyperparameter optimization
   - Automated feature engineering

3. **Improved Monitoring:**
   - Model drift detection
   - Anomaly detection
   - Explainability tools

4. **Security Enhancements:**
   - Fine-grained access control
   - Audit logging
   - Compliance reporting

## Conclusion

The NovaLux AI Model Server provides a robust foundation for the AI capabilities of the NovaLux AI Casino platform. With its scalable architecture, comprehensive monitoring, and integration with other components, it enables the Forever Growth Loop that powers the platform's self-evolution.

The implementation follows best practices for Kubernetes deployments, microservices architecture, and AI model serving, ensuring reliability, scalability, and security.
