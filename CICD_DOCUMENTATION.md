# CI/CD Pipeline Documentation

## Overview

This document explains the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Task Manager application.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CODE COMMIT                               │
│                   (Push to main/develop)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUILD STAGE                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Checkout Code                                          │  │
│  │ 2. Set up Python 3.11                                     │  │
│  │ 3. Install Dependencies (pip install -r requirements.txt) │  │
│  │ 4. Initialize Test Database                               │  │
│  │ 5. Run Code Linting (pylint)                              │  │
│  │ 6. Run Unit Tests (pytest)                                │  │
│  │ 7. Generate Coverage Reports                              │  │
│  │ 8. Publish Test Results                                   │  │
│  │ 9. Create Deployment Package (.zip)                       │  │
│  │ 10. Publish Build Artifacts                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    Build Success?
                         │
              ┌──────────┴──────────┐
              │                     │
           NO │                     │ YES
              │                     │
              ▼                     ▼
         ┌─────────┐      ┌──────────────────┐
         │  STOP   │      │ DEPLOY DECISION  │
         │ Failed  │      │  main branch?    │
         └─────────┘      └────────┬─────────┘
                                   │
                        ┌──────────┴──────────┐
                        │                     │
                     YES│                     │NO (develop)
                        │                     │
                        ▼                     ▼
        ┌────────────────────────┐   ┌──────────────────┐
        │  DEPLOY TO PRODUCTION  │   │ DEPLOY TO STAGING│
        │                        │   │   (Optional)     │
        │ 1. Download Artifacts  │   └──────────────────┘
        │ 2. Deploy to Azure     │
        │ 3. Configure Settings  │
        │ 4. Run Smoke Tests     │
        │ 5. Health Check        │
        └────────────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │   DEPLOYMENT SUCCESS   │
        │  App Live in Production│
        └────────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Build and Test

**Trigger:** Push to any branch, or Pull Request

**Steps:**

1. **Environment Setup**
   - Use Ubuntu Linux agent
   - Install Python 3.11
   - Verify Python and pip versions

2. **Dependency Installation**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Database Initialization**
   ```bash
   python init_db.py
   ```

4. **Code Quality**
   ```bash
   pylint app.py --disable=C,R,W
   ```
   - Checks for code errors
   - Non-blocking (continues even if warnings)

5. **Unit Testing**
   ```bash
   pytest tests/ --junitxml=junit/test-results.xml \
                  --cov=. \
                  --cov-report=xml \
                  --cov-report=html
   ```
   - Runs all tests in `tests/` directory
   - Generates JUnit XML for Azure DevOps
   - Creates coverage reports

6. **Test Results Publishing**
   - Publishes test results to Azure DevOps
   - Shows pass/fail status
   - Displays test duration
   - Blocks deployment if tests fail

7. **Coverage Reporting**
   - Publishes code coverage metrics
   - Shows line and branch coverage
   - Generates HTML reports

8. **Artifact Creation**
   - Creates a .zip file of the entire application
   - Includes all source code, templates, static files
   - Stores as build artifact for deployment

**Success Criteria:**
- All tests pass
- Code coverage > 80% (recommended)
- No critical lint errors
- Artifact created successfully

---

### Stage 2: Deploy to Production

**Trigger:** Push to `main` branch (after successful build)

**Pre-requisites:**
- Build stage completed successfully
- Running on `main` branch
- Service connection configured

**Steps:**

1. **Download Build Artifacts**
   - Retrieves the .zip package from Build stage
   - Ensures we deploy exactly what was tested

2. **Deploy to Azure App Service**
   - Uses Azure Web App task
   - Deploys to Linux App Service
   - Sets Python 3.11 runtime
   - Configures startup command: `gunicorn --bind=0.0.0.0 --timeout 600 app:app`

3. **Configure App Settings**
   - Sets environment variables:
     - `ENVIRONMENT=production`
     - `DB_TYPE=azure_sql`
     - `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
     - `WEBSITE_HTTPLOGGING_RETENTION_DAYS=7`

4. **Smoke Tests**
   - Waits for app to start
   - Calls `/health` endpoint
   - Verifies 200 OK response
   - Fails deployment if health check fails

**Success Criteria:**
- Deployment completes without errors
- App Service starts successfully
- Health check returns 200 OK
- Application accessible via HTTPS

---

### Stage 3: Deploy to Staging (Optional)

**Trigger:** Push to `develop` branch (after successful build)

**Purpose:**
- Test changes before production
- Integration testing
- Demo environment

---

## Pipeline Configuration

### File: `azure-pipelines.yml`

Located at project root, this file defines the entire pipeline.

**Key Sections:**

```yaml
trigger:
  branches:
    include:
      - main
      - develop
```
- Runs on pushes to main or develop
- Can add more branches as needed

```yaml
pr:
  branches:
    include:
      - main
      - develop
```
- Runs on Pull Requests
- Validates before merging

```yaml
pool:
  vmImage: 'ubuntu-latest'
```
- Uses Microsoft-hosted Ubuntu agent
- No maintenance required

```yaml
variables:
  pythonVersion: '3.11'
  azureSubscription: 'TaskManagerAzureConnection'
  webAppName: 'taskmanager-app'
  resourceGroup: 'taskmanager-rg'
```
- Centralized configuration
- Easy to update

---

## Environments

### Production Environment

- **Name:** `production`
- **Purpose:** Live application for end users
- **Protection:** Can add approval gates
- **Monitoring:** Application Insights enabled

### Staging Environment

- **Name:** `staging`
- **Purpose:** Testing before production
- **Protection:** Optional approvals
- **Monitoring:** Separate App Insights instance

---

## Testing Strategy

### Unit Tests (`pytest`)

**Location:** `tests/test_app.py`

**Coverage:**
- Route testing (GET/POST)
- Database operations
- Business logic
- Health checks

**Example:**
```python
def test_home_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
```

### Smoke Tests (`smoke_tests.py`)

**Purpose:** Post-deployment verification

**Tests:**
1. Health endpoint responds
2. Homepage loads
3. Static files accessible

**Usage:**
```bash
python smoke_tests.py https://your-app.azurewebsites.net
```

### Coverage Requirements

- **Target:** >80% code coverage
- **Measurement:** Line and branch coverage
- **Reports:** HTML and XML formats
- **Blocking:** Can configure to fail if below threshold

---

## Security

### Secrets Management

**Never commit:**
- Database passwords
- API keys
- Secret keys
- Connection strings

**Use Azure DevOps Variable Groups:**
1. Store secrets as secure variables
2. Reference in pipeline
3. Injected at runtime

**Example:**
```yaml
variables:
  - group: TaskManager-Secrets
```

### Service Connections

- Uses Azure Active Directory authentication
- Service principal with minimal permissions
- Scoped to specific resource group
- Rotatable credentials

---

## Monitoring & Observability

### Build Monitoring

**Azure DevOps Dashboard:**
- Build success rate
- Test pass rate
- Average build duration
- Failed builds trend

**Metrics to Track:**
- Builds per day
- Time to detect failures
- Time to fix failures
- Deployment frequency

### Deployment Monitoring

**Application Insights:**
- Deployment markers
- Performance after deployment
- Error rates
- User impact

**Health Checks:**
- `/health` endpoint
- Database connectivity
- Application version
- Environment verification

---

## Rollback Strategy

### Automatic Rollback

Not currently implemented, but recommended:

1. **Deployment Slots**
   - Deploy to staging slot
   - Warm up
   - Swap with production
   - Instant rollback if needed

2. **Health Check Failure**
   - If smoke tests fail
   - Deployment marked as failed
   - Previous version remains active

### Manual Rollback

```bash
# Via Azure CLI
az webapp deployment slot swap \
  --resource-group taskmanager-rg \
  --name taskmanager-app \
  --slot staging \
  --target-slot production

# Or redeploy previous version
az webapp deployment source sync \
  --resource-group taskmanager-rg \
  --name taskmanager-app
```

---

## Performance Optimization

### Caching (Future Enhancement)

```yaml
- task: Cache@2
  inputs:
    key: 'python | "$(Agent.OS)" | requirements.txt'
    path: $(PIP_CACHE_DIR)
    restoreKeys: |
      python | "$(Agent.OS)"
```

### Parallel Testing

```yaml
strategy:
  parallel: 4
```

### Build Artifacts

- Only include necessary files
- Exclude .git, tests, docs
- Compress to reduce size

---

## Troubleshooting

### Common Issues

**1. Build Fails - Dependencies**
```
ERROR: Could not find a version that satisfies the requirement...
```
**Solution:** Check requirements.txt versions, update if needed

**2. Tests Fail - Database**
```
ERROR: Database not initialized
```
**Solution:** Ensure init_db.py runs before tests

**3. Deployment Fails - Service Connection**
```
ERROR: Service connection not found
```
**Solution:** Check service connection name in variables

**4. Smoke Tests Fail - App Not Ready**
```
ERROR: Connection refused
```
**Solution:** Increase warmup time before smoke tests

### Debug Mode

Add this to pipeline for debugging:

```yaml
- script: |
    echo "Python version: $(python --version)"
    echo "Working directory: $(pwd)"
    echo "Files: $(ls -la)"
  displayName: 'Debug Information'
```

---

## Best Practices

### ✅ DO

- Run tests on every commit
- Use secrets for sensitive data
- Monitor build success rates
- Keep builds fast (<5 minutes)
- Use caching for dependencies
- Tag releases
- Document pipeline changes
- Review failed builds promptly

### ❌ DON'T

- Commit secrets to code
- Skip tests to speed up builds
- Deploy without smoke tests
- Use personal accounts for service connections
- Ignore flaky tests
- Deploy on Fridays (joke, but...)

---

## Metrics & KPIs

### Pipeline Health

| Metric | Target | Current |
|--------|--------|---------|
| Build Success Rate | >95% | Track |
| Average Build Time | <5 min | Track |
| Test Pass Rate | 100% | Track |
| Deployment Success Rate | >98% | Track |
| Time to Deploy | <10 min | Track |

### Deployment Frequency

- **Goal:** Multiple times per day (for mature projects)
- **Sprint 4:** At least once per sprint
- **Production:** On-demand or scheduled

---

## Future Enhancements

1. **Blue-Green Deployment**
   - Zero-downtime deployments
   - Instant rollback

2. **Canary Releases**
   - Gradual rollout
   - Monitor for issues

3. **Automated Performance Tests**
   - Load testing
   - Response time validation

4. **Security Scanning**
   - Dependency vulnerability checks
   - Code security analysis

5. **Infrastructure as Code**
   - Terraform/Bicep for Azure resources
   - Version controlled infrastructure

---

## Team Workflow

### Developer Workflow

1. Create feature branch
2. Make changes
3. Commit and push
4. Pipeline runs automatically
5. Review test results
6. Create Pull Request
7. Pipeline validates PR
8. Code review by team
9. Merge to main
10. Automatic deployment

### Release Process

1. Merge feature to develop
2. Test in staging
3. Create release PR to main
4. Final review
5. Merge triggers production deployment
6. Monitor deployment
7. Verify in production
8. Tag release

---

## Quick Commands

```bash
# Local testing before push
python -m pytest tests/ -v

# Check what will be deployed
git diff main

# View pipeline status
az pipelines runs list --project TaskManager

# Manual trigger
az pipelines run --name "TaskManager-CI"

# View logs
az pipelines runs show --id <run-id>
```

---

## Documentation Links

- [Azure Pipelines Docs](https://docs.microsoft.com/azure/devops/pipelines/)
- [YAML Schema](https://docs.microsoft.com/azure/devops/pipelines/yaml-schema)
- [Azure App Service Deployment](https://docs.microsoft.com/azure/app-service/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Last Updated:** November 30, 2025  
**Version:** 1.0  
**Maintained By:** Development Team
