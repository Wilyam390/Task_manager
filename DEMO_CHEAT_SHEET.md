# 🎯 QUICK REFERENCE - Demo Day Cheat Sheet

**PRINT THIS OR KEEP IT VISIBLE DURING DEMO**

---

## ⚡ QUICK COMMANDS

```bash
# Setup (run 30 min before demo)
cd /Users/leenabarq/Documents/Task_manager
source venv/bin/activate
pip install -q Flask Werkzeug python-dotenv pytest gunicorn requests prometheus-client
rm -f tasks.db && python init_db.py
pytest tests/ -v
python app.py

# URLs to visit
http://localhost:8000           # Main app
http://localhost:8000/health    # Health check
http://localhost:8000/metrics   # Prometheus metrics
```

---

## 📊 KEY NUMBERS TO REMEMBER

- **5** Azure services (need 3+) ✅
- **74%** test coverage (need 70%+) ✅
- **18** tests passing (all green) ✅
- **4** sprints completed ✅
- **100%** sprint velocity ✅
- **16** user stories (13 complete) ✅
- **10-12** minute demo ✅

---

## 🎤 OPENING LINE

> "Good morning! We're presenting our Task Manager - a cloud-native application built with Azure and modern DevOps practices. Over 4 Scrum sprints, we delivered a production-ready MVP with automated testing, CI/CD, and comprehensive monitoring."

---

## 💻 DEMO SEQUENCE (4 min)

1. **Add task:** "Prepare final demo" (with due date)
2. **Add task:** "Complete documentation" (yesterday - shows red)
3. **Filter:** Click All/Active/Completed buttons
4. **Search:** Type "demo" in search box
5. **Toggle:** Mark first task complete
6. **Delete:** Remove one task
7. **Health:** Show http://localhost:8000/health
8. **Metrics:** Show http://localhost:8000/metrics

---

## 🏗️ ARCHITECTURE (memorize this)

```
User → Azure App Service (Flask) → Azure SQL Database
              ↓
        Application Insights → Azure Monitor
              ↓
        GitHub Actions (CI/CD)
```

**5 Azure Services:**
1. App Service (hosting)
2. SQL Database (data)
3. Application Insights (monitoring)
4. Azure Monitor (dashboards)
5. GitHub Actions (CI/CD)

---

## 📋 WHERE TO FIND THINGS

| What | Where |
|------|-------|
| Product Backlog | SCRUM_DOCUMENTATION.md line 12 |
| Sprint Reviews | SCRUM_DOCUMENTATION.md (each sprint section) |
| Retrospectives | SCRUM_DOCUMENTATION.md (each sprint section) |
| Definition of Done | SCRUM_DOCUMENTATION.md line 438 |
| Architecture | README.md line 12 |
| Test Results | Run: `pytest tests/ -v` |
| CI/CD Pipeline | GitHub → Actions tab |

---

## ❓ TOP 5 EXPECTED QUESTIONS

### Q1: "Why Flask?"
**A:** Lightweight, perfect for MVPs, team had Python experience.

### Q2: "Biggest challenge?"
**A:** Azure SQL configuration. Solved with database abstraction layer.

### Q3: "Is it deployed to Azure?"
**A:** Complete CI/CD pipeline ready. Demoing locally, but one-click deployment available.

### Q4: "How scale this?"
**A:** Auto-scaling, Redis cache, read replicas, CDN, AKS if needed.

### Q5: "Why not 100% coverage?"
**A:** Focused on critical paths. 74% meets standards. Some Azure paths hard to test locally.

---

## 🎯 KEY MESSAGES

1. ✅ **It works** - Fully functional MVP
2. ✅ **It's tested** - 74% coverage, 18 tests
3. ✅ **It's automated** - Full CI/CD pipeline
4. ✅ **It's monitored** - Health, metrics, logs
5. ✅ **It's documented** - Complete Scrum artifacts
6. ✅ **It exceeds requirements** - 5 services, Docker, enhanced features

---

## 🚨 IF THINGS GO WRONG

### App won't start?
→ Show screenshots + code walkthrough

### Internet down?
→ Everything works offline (local demo)

### Forgot something?
→ Check DEMO_SCRIPT.md or README.md

### Can't answer question?
→ "Let me consult with team..." OR "I'll follow up after"

---

## 📂 FILES TO HAVE OPEN

- [ ] Terminal running app
- [ ] Browser at localhost:8000
- [ ] GitHub repo (Actions tab)
- [ ] SCRUM_DOCUMENTATION.md
- [ ] README.md
- [ ] This cheat sheet

---

## ⏱️ TIME MANAGEMENT

- Introduction: 1 min
- Architecture: 2 min
- **LIVE DEMO: 4 min** ← Most important!
- DevOps: 2 min
- Testing: 1 min
- Scrum: 1 min
- Wrap-up: 1 min

**IF RUNNING OVER:** Skip monitoring details

---

## 💪 CONFIDENCE BOOSTERS

- ✅ All tests pass
- ✅ All requirements met
- ✅ 100% sprint completion
- ✅ Professional documentation
- ✅ Working application
- ✅ You've got this!

---

## 🎬 LAST THING BEFORE DEMO

**Deep breath. You're ready. The work is done. Just show what you built!**

---

**GOOD LUCK! 🚀**
