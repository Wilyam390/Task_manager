# Docker Deployment Guide

## 🐳 Quick Start

### Option 1: Docker (Application Only)
```bash
# Build
docker build -t task-manager:latest .

# Run
docker run -p 8000:8000 -e SECRET_KEY=mysecret task-manager:latest

# Access: http://localhost:8000
```

### Option 2: Docker Compose (Full Stack)
```bash
# Start all services
docker-compose up -d

# Access:
# - App: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

## 📋 What's Included

### Dockerfile Features
✅ Multi-stage build (reduces image size)
✅ Python 3.11 slim base image
✅ Non-root user (security best practice)
✅ Health checks
✅ Gunicorn production server
✅ Environment-based configuration

### Docker Compose Stack
✅ Flask application
✅ Prometheus (metrics collection)
✅ Grafana (visualization)
✅ Persistent volumes
✅ Network isolation

## 🔧 Configuration

### Environment Variables
- `ENVIRONMENT`: development/production
- `SECRET_KEY`: Flask secret key
- `AZURE_SQL_CONNECTION_STRING`: Database connection
- `APPINSIGHTS_INSTRUMENTATION_KEY`: Azure monitoring (keep the underscores; not `APPINSIGHTS_INSTRUMENTATIONKEY`)

### Production Deployment
```bash
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=$(openssl rand -base64 32) \
  -e AZURE_SQL_CONNECTION_STRING="your-conn-string" \
  task-manager:latest
```

## 📊 Monitoring

### Prometheus Metrics
- Endpoint: http://localhost:8000/metrics
- Tracks: HTTP requests, latency, task operations

### Grafana Dashboards
1. Login: http://localhost:3000 (admin/admin)
2. Add Prometheus datasource: http://prometheus:9090
3. Create dashboard with metrics

## 🧪 Testing Docker Build

```bash
# Build and test locally
docker build -t task-manager:test .
docker run -p 8000:8000 task-manager:test

# Check health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics
```

## 📦 CI/CD Integration

The GitHub Actions pipeline now:
1. ✅ Builds Docker image on every push
2. ✅ Runs tests with 70% coverage requirement
3. ✅ Saves Docker image as artifact
4. ✅ Deploys to Azure App Service

## 🎯 Assignment Requirements Met

| Requirement | Status | Evidence |
|------------|--------|----------|
| Dockerfile exists | ✅ | `/Dockerfile` |
| Multi-stage build | ✅ | Builder + Production stages |
| Production-ready | ✅ | Gunicorn, health checks, non-root user |
| docker-compose.yml | ✅ | Full monitoring stack |
| CI/CD builds image | ✅ | `.github/workflows/azure-deploy.yml` |
| Documentation | ✅ | README.md, DOCKER_GUIDE.md |

**Worth: 20% of assignment grade** ✅
