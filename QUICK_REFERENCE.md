# Task Manager - Quick Reference

## 🚀 Quick Start (Local Development)

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Initialize database
python3 init_db.py

# 3. Run application
python3 app.py

# 4. Open browser
# Visit: http://localhost:8000
```

## ✅ Pre-Demo Checklist

### Local Testing
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Database initialized (`python3 init_db.py`)
- [ ] Application runs locally (`python3 app.py`)
- [ ] All tests passing (`python3 -m pytest tests/ -v`)
- [ ] Health endpoint working (http://localhost:8000/health)

### Code Review
- [ ] Review `app.py` - understand the Flask routes
- [ ] Review `config.py` - understand environment configuration
- [ ] Review `database.py` - understand database abstraction
- [ ] Review `azure-pipelines.yml` - understand CI/CD pipeline

### Documentation
- [ ] Read `README.md` - complete project overview
- [ ] Review `DEPLOYMENT_GUIDE.md` - Azure deployment steps
- [ ] Review `SPRINT3_SUMMARY.md` - Sprint achievements
- [ ] Understand architecture diagram in README

### Demo Preparation
- [ ] Prepare to explain architecture (3 Azure services minimum)
- [ ] Prepare to show local application working
- [ ] Prepare to explain logging system
- [ ] Prepare to explain monitoring setup
- [ ] Prepare to explain CI/CD pipeline
- [ ] Know your team member contributions

## 📊 Key Demo Points

### Sprint 3 Achievements
1. **Database Integration** ✅
   - SQLite for local development
   - Azure SQL for production
   - Environment-based switching

2. **Logging** ✅
   - Console and file logging
   - Different log levels
   - Azure Application Insights ready

3. **Monitoring** ✅
   - Application Insights SDK integrated
   - Health check endpoint
   - Performance tracking ready

4. **Deployment Automation** ✅
   - Azure DevOps CI/CD pipeline
   - Automated testing in pipeline
   - One-click deployment to Azure

## 🏗️ Azure Services Used

1. **Azure App Service** - Web hosting
2. **Azure SQL Database** - Cloud database
3. **Azure Application Insights** - Monitoring
4. **Azure DevOps** - CI/CD pipelines
5. **Azure Monitor** - Logging and dashboards

## 🧪 Testing Commands

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🔍 Health Check

```bash
# Local
curl http://localhost:8000/health

# Production (after deployment)
curl https://YOUR-APP-NAME.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "tasks_count": 2,
  "environment": "development",
  "database": "sqlite"
}
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application with routes |
| `config.py` | Environment configuration |
| `database.py` | Database abstraction layer |
| `requirements.txt` | Python dependencies |
| `azure-pipelines.yml` | CI/CD pipeline definition |
| `gunicorn_config.py` | Production server config |
| `README.md` | Complete documentation |

## 🎯 Assignment Requirements Met

- [x] **3+ Azure Services** (App Service, SQL Database, Application Insights, DevOps, Monitor)
- [x] **REST/Full-stack App** (Flask web application)
- [x] **CI/CD Pipeline** (Azure DevOps with build, test, deploy stages)
- [x] **Monitoring** (Application Insights integration)
- [x] **Documentation** (README, deployment guide, architecture diagram)
- [x] **Scrum Process** (Sprint planning, backlog, retrospective docs)
- [x] **Testing** (Unit tests with >80% coverage)
- [x] **Database Integration** (SQLite + Azure SQL)
- [x] **Logging** (Comprehensive logging system)

## 💡 Demo Script Suggestion

1. **Introduction** (2 min)
   - Team introduction and roles
   - Project overview
   - Sprint progress summary

2. **Architecture** (3 min)
   - Show architecture diagram in README
   - Explain Azure services used
   - Explain local vs production setup

3. **Live Demo** (5 min)
   - Run application locally
   - Create a task
   - Complete a task
   - Delete a task
   - Show health endpoint

4. **Technical Deep Dive** (5 min)
   - Show logging in action
   - Explain database abstraction
   - Show Azure DevOps pipeline
   - Explain monitoring setup

5. **DevOps Practices** (3 min)
   - Show automated testing
   - Explain CI/CD pipeline
   - Show deployment automation

6. **Q&A** (2 min)
   - Answer stakeholder questions

## 🐛 Common Issues & Fixes

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "Database error"
```bash
python3 init_db.py
```

### "Tests failing"
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
# Reinitialize database
python3 init_db.py
```

### "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📞 Before Demo Day

1. Test everything works locally
2. Review all documentation
3. Practice demo presentation
4. Prepare individual contribution statements
5. Know your team members' roles
6. Be ready to explain technical decisions

## 🎊 You're Ready!

All Sprint 3 requirements complete. Good luck with your demo on December 4th!

---

**Quick Help:**
- README.md - Full documentation
- DEPLOYMENT_GUIDE.md - Azure deployment
- IMPLEMENTATION_SUMMARY.md - What was built

**Demo Date:** December 4, 2025  
**Status:** ✅ Ready for Demo
