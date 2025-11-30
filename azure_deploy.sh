#!/bin/bash

# Azure Deployment Script for Task Manager
# Resource Group: BCSAI2025-DEVOPS-STUDENT-8B
# Location: westeurope

# Configuration
RESOURCE_GROUP="BCSAI2025-DEVOPS-STUDENT-8B"
LOCATION="westeurope"
APP_NAME="task-manager-8b"
PLAN_NAME="task-manager-plan-8b"
SQL_SERVER_NAME="task-manager-sql-8b"
SQL_DB_NAME="taskmanagerdb"
SQL_ADMIN_USER="sqladmin"
SQL_ADMIN_PASSWORD="TaskManager2025!"
APPINSIGHTS_NAME="task-manager-insights-8b"

echo "🚀 Starting Azure Deployment for Task Manager..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Step 1: Create App Service Plan (Linux, Python)
echo "📦 Creating App Service Plan..."
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux \
  --output table

# Step 2: Create Web App
echo ""
echo "🌐 Creating Web App..."
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "PYTHON:3.11" \
  --output table

# Step 3: Configure Web App settings
echo ""
echo "⚙️  Configuring Web App settings..."
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app" \
  --output table

# Step 4: Create Azure SQL Server
echo ""
echo "🗄️  Creating Azure SQL Server..."
az sql server create \
  --name $SQL_SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $SQL_ADMIN_USER \
  --admin-password $SQL_ADMIN_PASSWORD \
  --output table

# Step 5: Configure SQL Server firewall (allow Azure services)
echo ""
echo "🔥 Configuring SQL Server firewall..."
az sql server firewall-rule create \
  --server $SQL_SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0 \
  --output table

# Step 6: Create SQL Database
echo ""
echo "💾 Creating SQL Database..."
az sql db create \
  --server $SQL_SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --name $SQL_DB_NAME \
  --service-objective S0 \
  --output table

# Step 7: Create Application Insights
echo ""
echo "📊 Creating Application Insights..."
az monitor app-insights component create \
  --app $APPINSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web \
  --output table

# Step 8: Get Application Insights Instrumentation Key
echo ""
echo "🔑 Retrieving Application Insights key..."
APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app $APPINSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

echo "Instrumentation Key: $APPINSIGHTS_KEY"

# Step 9: Build SQL connection string
SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:$SQL_SERVER_NAME.database.windows.net,1433;Database=$SQL_DB_NAME;Uid=$SQL_ADMIN_USER;Pwd=$SQL_ADMIN_PASSWORD;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Step 10: Configure Web App environment variables
echo ""
echo "🔧 Setting environment variables..."
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    FLASK_ENV="production" \
    DB_TYPE="azure_sql" \
    AZURE_SQL_CONNECTION_STRING="$SQL_CONNECTION_STRING" \
    APPINSIGHTS_INSTRUMENTATIONKEY="$APPINSIGHTS_KEY" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
  --output table

# Step 11: Enable logging
echo ""
echo "📝 Enabling application logging..."
az webapp log config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --web-server-logging filesystem \
  --output table

# Step 12: Deploy application
echo ""
echo "🚢 Deploying application code..."
az webapp up \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --runtime "PYTHON:3.11" \
  --sku B1 \
  --location $LOCATION

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Resource Summary:"
echo "  Web App URL: https://$APP_NAME.azurewebsites.net"
echo "  SQL Server: $SQL_SERVER_NAME.database.windows.net"
echo "  Database: $SQL_DB_NAME"
echo "  App Insights: $APPINSIGHTS_NAME"
echo ""
echo "🔍 Next Steps:"
echo "  1. Initialize database: Run init_db.py with Azure SQL connection"
echo "  2. Visit: https://$APP_NAME.azurewebsites.net"
echo "  3. Monitor logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
