# Azure Deployment Quick Start Guide

This guide will help you deploy the Task Manager application to Azure in under 30 minutes.

## Prerequisites Checklist

- [ ] Azure subscription (student account works)
- [ ] Azure CLI installed (`az --version` to check)
- [ ] Git installed
- [ ] Python 3.11+ installed
- [ ] Code pushed to GitHub/Azure Repos

## Step-by-Step Deployment

### 1. Login to Azure

```bash
az login
```

### 2. Set Your Subscription (if you have multiple)

```bash
# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

### 3. Create Resource Group

```bash
az group create \
  --name taskmanager-rg \
  --location eastus
```

### 4. Create App Service Plan (Linux)

```bash
az appservice plan create \
  --name taskmanager-plan \
  --resource-group taskmanager-rg \
  --sku B1 \
  --is-linux
```

### 5. Create Web App

```bash
az webapp create \
  --resource-group taskmanager-rg \
  --plan taskmanager-plan \
  --name taskmanager-app-YOURNAME \
  --runtime "PYTHON:3.11"
```

**Note:** Replace `YOURNAME` with something unique (web app names must be globally unique)

### 6. Create Azure SQL Server

```bash
az sql server create \
  --name taskmanager-sql-YOURNAME \
  --resource-group taskmanager-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password "YourStrongP@ssw0rd123"
```

### 7. Configure SQL Server Firewall

```bash
# Allow Azure services
az sql server firewall-rule create \
  --resource-group taskmanager-rg \
  --server taskmanager-sql-YOURNAME \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your IP (for management)
az sql server firewall-rule create \
  --resource-group taskmanager-rg \
  --server taskmanager-sql-YOURNAME \
  --name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### 8. Create SQL Database

```bash
az sql db create \
  --resource-group taskmanager-rg \
  --server taskmanager-sql-YOURNAME \
  --name taskmanager-db \
  --service-objective S0
```

### 9. Create Application Insights

```bash
az monitor app-insights component create \
  --app taskmanager-insights \
  --location eastus \
  --resource-group taskmanager-rg \
  --application-type web
```

### 10. Get Application Insights Key

```bash
az monitor app-insights component show \
  --app taskmanager-insights \
  --resource-group taskmanager-rg \
  --query instrumentationKey \
  --output tsv
```

**Save this key!** You'll need it in the next step.

### 11. Configure Web App Settings

```bash
az webapp config appsettings set \
  --resource-group taskmanager-rg \
  --name taskmanager-app-YOURNAME \
  --settings \
    ENVIRONMENT=production \
    DB_TYPE=azure_sql \
    AZURE_SQL_SERVER=taskmanager-sql-YOURNAME.database.windows.net \
    AZURE_SQL_DATABASE=taskmanager-db \
    AZURE_SQL_USERNAME=sqladmin \
    AZURE_SQL_PASSWORD="YourStrongP@ssw0rd123" \
    APPINSIGHTS_INSTRUMENTATION_KEY="YOUR_KEY_FROM_STEP_10" \
    SECRET_KEY="your-secret-key-change-this" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 12. Set Startup Command

```bash
az webapp config set \
  --resource-group taskmanager-rg \
  --name taskmanager-app-YOURNAME \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

### 13. Deploy from Local Git (Option A)

```bash
# Get deployment credentials
az webapp deployment list-publishing-credentials \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg

# Get Git URL
az webapp deployment source config-local-git \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg

# Add Azure remote
git remote add azure <GIT_URL_FROM_ABOVE>

# Push to deploy
git push azure main
```

### 14. Deploy from GitHub (Option B)

```bash
az webapp deployment source config \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg \
  --repo-url https://github.com/YOUR_USERNAME/Task_Manager \
  --branch main \
  --manual-integration
```

### 15. Initialize Database

Connect to your Azure SQL database and run the schema:

```bash
# Install sqlcmd if needed
# Then connect:
sqlcmd -S taskmanager-sql-YOURNAME.database.windows.net \
  -d taskmanager-db \
  -U sqladmin \
  -P "YourStrongP@ssw0rd123"

# In sqlcmd, paste the SQL from schema.sql (adapted for SQL Server):
CREATE TABLE tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX),
    completed BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE()
);
GO
```

### 16. Verify Deployment

```bash
# Open in browser
az webapp browse \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg

# Check health endpoint
curl https://taskmanager-app-YOURNAME.azurewebsites.net/health

# Stream logs
az webapp log tail \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg
```

## Troubleshooting

### App won't start
```bash
# Check logs
az webapp log tail --name taskmanager-app-YOURNAME --resource-group taskmanager-rg

# Check configuration
az webapp config appsettings list \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg
```

### Database connection fails
- Check firewall rules allow Azure services
- Verify connection string in app settings
- Ensure database exists and schema is created

### Can't access website
- Check if app is running: `az webapp show --name taskmanager-app-YOURNAME --resource-group taskmanager-rg`
- Check if domain is correct: `https://taskmanager-app-YOURNAME.azurewebsites.net`

## Monitoring

### View in Azure Portal
1. Go to https://portal.azure.com
2. Navigate to your resource group: `taskmanager-rg`
3. Click on Application Insights: `taskmanager-insights`
4. Explore metrics, logs, and performance data

### Stream Logs
```bash
az webapp log tail \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg
```

### Download Logs
```bash
az webapp log download \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg \
  --log-file logs.zip
```

## Clean Up (When Done)

**WARNING:** This will delete everything!

```bash
az group delete \
  --name taskmanager-rg \
  --yes \
  --no-wait
```

## Quick Commands Reference

```bash
# Restart app
az webapp restart --name taskmanager-app-YOURNAME --resource-group taskmanager-rg

# Stop app
az webapp stop --name taskmanager-app-YOURNAME --resource-group taskmanager-rg

# Start app
az webapp start --name taskmanager-app-YOURNAME --resource-group taskmanager-rg

# View app URL
az webapp show --name taskmanager-app-YOURNAME --resource-group taskmanager-rg --query defaultHostName

# Update app setting
az webapp config appsettings set \
  --name taskmanager-app-YOURNAME \
  --resource-group taskmanager-rg \
  --settings KEY=VALUE
```

## Cost Optimization

Current setup costs approximately:
- App Service (B1): ~$13/month
- SQL Database (S0): ~$15/month
- Application Insights: Free tier included
- **Total: ~$28/month**

For students: Use Azure for Students credit ($100)

## Next Steps

1. ✅ Set up Azure DevOps pipeline for automated deployments
2. ✅ Configure monitoring alerts
3. ✅ Set up custom domain (optional)
4. ✅ Enable SSL/HTTPS (automatic with Azure)
5. ✅ Configure backup policies

---

**Need Help?**
- Azure Documentation: https://docs.microsoft.com/azure
- Azure CLI Reference: https://docs.microsoft.com/cli/azure
- Contact your team's DevOps lead

**Last Updated:** November 30, 2025
