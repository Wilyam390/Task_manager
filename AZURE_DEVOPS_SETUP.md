# Azure DevOps CI/CD Setup Guide

Complete guide to setting up automated deployment for the Task Manager application.

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] Azure account with active subscription
- [ ] Azure DevOps organization (free tier works)
- [ ] GitHub account (or Azure Repos)
- [ ] Your code pushed to a repository
- [ ] Azure resources created (App Service, SQL Database, etc.)

---

## Part 1: Create Azure DevOps Project

### Step 1: Create Organization (if needed)

1. Go to https://dev.azure.com
2. Click "Start free" or sign in
3. Create a new organization:
   - Name: `your-org-name`
   - Region: Choose your preferred region

### Step 2: Create Project

1. Click **"+ New project"**
2. Fill in details:
   - **Project name:** `TaskManager`
   - **Visibility:** Private (recommended)
   - **Version control:** Git
   - **Work item process:** Agile
3. Click **"Create"**

---

## Part 2: Connect to Your Repository

### Option A: Use GitHub Repository

1. In your project, go to **Pipelines**
2. Click **"Create Pipeline"**
3. Select **"GitHub"**
4. Authorize Azure Pipelines to access GitHub
5. Select your repository: `Wilyam390/Task_Manager`
6. Azure DevOps will detect `azure-pipelines.yml`

### Option B: Use Azure Repos

1. Go to **Repos** → **Files**
2. Click **"Import a repository"**
3. Enter your GitHub URL
4. Click **"Import"**

---

## Part 3: Create Service Connection to Azure

This allows Azure DevOps to deploy to your Azure subscription.

### Step 1: Get Azure Subscription Details

```bash
# Login to Azure
az login

# List subscriptions
az account list --output table

# Note your Subscription ID
```

### Step 2: Create Service Connection

1. In Azure DevOps, go to **Project Settings** (bottom left)
2. Under **Pipelines**, click **"Service connections"**
3. Click **"New service connection"**
4. Select **"Azure Resource Manager"**
5. Click **"Next"**

### Step 3: Configure Service Connection

**Authentication method:** Service principal (automatic)

1. **Scope level:** Subscription
2. **Subscription:** Select your Azure subscription
3. **Resource group:** Select `taskmanager-rg` (or leave empty for full access)
4. **Service connection name:** `TaskManagerAzureConnection`
5. **Grant access permission to all pipelines:** ✅ Check this
6. Click **"Save"**

### Step 4: Update Pipeline Variables

Edit `azure-pipelines.yml` and update:

```yaml
variables:
  azureSubscription: 'TaskManagerAzureConnection'  # Your service connection name
  webAppName: 'taskmanager-app-yourname'           # Your App Service name
  resourceGroup: 'taskmanager-rg'                  # Your resource group name
```

---

## Part 4: Configure Pipeline Variables

### Option 1: In the YAML file (for non-sensitive values)

Already set in `azure-pipelines.yml`:
- `pythonVersion`
- `buildConfiguration`

### Option 2: In Azure DevOps UI (for sensitive values)

1. Go to **Pipelines** → **Library**
2. Click **"+ Variable group"**
3. Name: `TaskManager-Config`
4. Add variables:

| Variable Name | Value | Secret? |
|--------------|-------|---------|
| `AZURE_SQL_PASSWORD` | Your SQL password | ✅ Yes |
| `SECRET_KEY` | Your Flask secret key | ✅ Yes |
| `APPINSIGHTS_KEY` | Your App Insights key | ✅ Yes |

5. Click **"Save"**

### Link Variable Group to Pipeline

Add to `azure-pipelines.yml`:

```yaml
variables:
  - group: TaskManager-Config  # Add this line
  - name: pythonVersion
    value: '3.11'
  # ... rest of your variables
```

---

## Part 5: Configure Environments

Environments provide deployment history and protection.

### Create Production Environment

1. Go to **Pipelines** → **Environments**
2. Click **"Create environment"**
3. Name: `production`
4. Resource: None (click **"Create"**)
5. Optional: Add approvals
   - Click **"..."** → **"Approvals and checks"**
   - Add **"Approvals"**
   - Select approvers
   - Click **"Create"**

### Create Staging Environment (Optional)

1. Repeat above steps with name: `staging`

---

## Part 6: Create and Run the Pipeline

### Step 1: Create Pipeline

1. Go to **Pipelines** → **Pipelines**
2. Click **"New pipeline"** (or "Create Pipeline")
3. Select your code location:
   - **GitHub** (recommended if using GitHub)
   - **Azure Repos Git**
4. Select your repository
5. Select **"Existing Azure Pipelines YAML file"**
6. Path: `/azure-pipelines.yml`
7. Click **"Continue"**

### Step 2: Review and Run

1. Review the pipeline YAML
2. Click **"Run"**
3. Watch the pipeline execute!

### Step 3: Monitor Pipeline

You'll see stages execute:
1. ✅ **Build** - Install dependencies, run tests
2. ✅ **DeployProduction** - Deploy to Azure (only on main branch)

---

## Part 7: Configure Branch Policies (Recommended)

Require pull requests and successful builds before merging.

1. Go to **Repos** → **Branches**
2. Find `main` branch, click **"..."** → **"Branch policies"**
3. Configure:
   - ✅ **Require a minimum number of reviewers:** 1
   - ✅ **Check for linked work items:** Optional
   - ✅ **Build Validation:**
     - Add build policy
     - Select your pipeline
     - Trigger: Automatic
     - Policy requirement: Required
   - ✅ **Limit merge types:** Squash merge only
4. Click **"Save"**

---

## Part 8: Test the Pipeline

### Test Automated Deployment

1. **Make a code change:**
   ```bash
   # Make a small change to README.md
   echo "Pipeline test" >> README.md
   git add README.md
   git commit -m "Test CI/CD pipeline"
   git push origin main
   ```

2. **Watch the pipeline:**
   - Go to **Pipelines** → **Pipelines**
   - Click on the running pipeline
   - Watch each stage execute

3. **Verify deployment:**
   ```bash
   # Check health endpoint
   curl https://your-app-name.azurewebsites.net/health
   ```

### Test Pull Request Build

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/test-pr
   echo "PR test" >> README.md
   git add README.md
   git commit -m "Test PR build"
   git push origin feature/test-pr
   ```

2. **Create Pull Request:**
   - Go to **Repos** → **Pull requests**
   - Click **"New pull request"**
   - Source: `feature/test-pr`
   - Target: `main`
   - Click **"Create"**

3. **Watch PR validation:**
   - Pipeline runs automatically
   - Merge is blocked until build succeeds

---

## Part 9: View Build Results

### Test Results

1. Go to **Pipelines** → **Pipelines**
2. Click on a completed run
3. Click on **"Tests"** tab
4. View:
   - Total tests run
   - Passed/Failed
   - Test duration
   - Coverage reports

### Code Coverage

1. In the pipeline run
2. Click **"Code Coverage"** tab
3. View:
   - Line coverage percentage
   - Branch coverage
   - Download detailed reports

### Artifacts

1. In the pipeline run
2. Click **"1 published"** under artifacts
3. Download the deployment package

---

## Part 10: Configure Notifications

### Email Notifications

1. Go to **Project Settings** → **Notifications**
2. Click **"New subscription"**
3. Select triggers:
   - **Build completed**
   - **Build failed**
   - **Release deployment completed**
4. Enter email addresses
5. Click **"Finish"**

### Slack/Teams Integration (Optional)

1. Install Azure Pipelines app in Slack/Teams
2. Configure webhook in Azure DevOps
3. Set up notification rules

---

## Part 11: Troubleshooting

### Pipeline Fails at Build Stage

**Problem:** Dependencies not installing

**Solution:**
```bash
# Check requirements.txt is correct
# Ensure Python version matches
```

### Pipeline Fails at Deploy Stage

**Problem:** Service connection not working

**Solution:**
1. Check service connection in Project Settings
2. Verify Azure subscription is active
3. Re-authorize if needed

### App Not Starting After Deployment

**Problem:** Missing environment variables

**Solution:**
1. Go to Azure Portal
2. App Service → Configuration
3. Add application settings:
   - `DB_TYPE=azure_sql`
   - `AZURE_SQL_SERVER=...`
   - `AZURE_SQL_PASSWORD=...`
   - etc.

### Tests Failing

**Problem:** Test database not initialized

**Solution:**
- Ensure `init_db.py` runs in pipeline
- Check test database path

---

## Part 12: Best Practices

### Security

- ✅ Store secrets in Variable Groups (marked as secret)
- ✅ Use service principals, not personal accounts
- ✅ Enable branch policies on main/develop
- ✅ Require code reviews

### Performance

- ✅ Cache dependencies (add caching task)
- ✅ Run tests in parallel when possible
- ✅ Use artifacts for deployment, not git checkout

### Reliability

- ✅ Add smoke tests after deployment
- ✅ Configure health checks
- ✅ Set up rollback strategies
- ✅ Monitor deployment success rates

---

## Quick Reference Commands

```bash
# View pipeline runs
az pipelines runs list --organization https://dev.azure.com/your-org --project TaskManager

# Trigger pipeline manually
az pipelines run --organization https://dev.azure.com/your-org --project TaskManager --name "TaskManager-CI"

# View pipeline definition
az pipelines show --organization https://dev.azure.com/your-org --project TaskManager --name "TaskManager-CI"

# Cancel pipeline run
az pipelines runs cancel --organization https://dev.azure.com/your-org --project TaskManager --id <run-id>
```

---

## Checklist

Before demo, verify:

- [ ] Pipeline created in Azure DevOps
- [ ] Service connection configured
- [ ] Variables set (including secrets)
- [ ] Environments created
- [ ] Pipeline runs successfully
- [ ] Tests pass in pipeline
- [ ] Deployment succeeds
- [ ] App works after deployment
- [ ] Smoke tests pass
- [ ] Branch policies configured
- [ ] Team members have access

---

## Success Criteria

Your CI/CD is working when:

1. ✅ Push to `main` triggers automatic build
2. ✅ All tests pass in build stage
3. ✅ App deploys automatically to Azure
4. ✅ Smoke tests verify deployment
5. ✅ Pull requests trigger builds
6. ✅ Failed builds block PR merging
7. ✅ Team receives notifications

---

## Next Steps

Once CI/CD is working:

1. **Add more tests** - Increase coverage
2. **Add deployment slots** - Blue/green deployment
3. **Set up staging** - Test before production
4. **Configure monitoring** - Track deployments in App Insights
5. **Add performance tests** - Load testing
6. **Set up alerts** - Notify on failures

---

**Created:** November 30, 2025  
**For:** Task Manager Sprint 4  
**Demo Date:** December 4, 2025

**Need help?** Check Azure DevOps documentation at https://docs.microsoft.com/azure/devops/
