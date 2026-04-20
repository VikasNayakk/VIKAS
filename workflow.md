# ACC Workflows — Quick Reference
**Source:** `Docs/ACC/ACC.Workflows.Guide.md` (Full Detail)  
**Version:** 26.04.01 | **Date:** 2026-04-14

---

## Invocation Format
```
Workflow("WorkflowId", "Targets", "Description")
```

---

# 1. Content Creation

| # | WorkflowId | Purpose | Targets Example |
|---|-----------|---------|-----------------|
| 1.1 | `Blog_Article` | Original blog articles likhta hai (EN/HIEN/HI) | `"Article_Slug"` ya `"Articles.csv"` |
| 1.2 | `Blog_ACLE` | Blog articles → ACLE cinematic video lessons | `"HIEN.csv"` ya `"EN/Slug"` |
| 1.3 | `Blogs_New` | Third-party blogs scrape + translate (EN/HIEN/HI) | `"healthline.com"` ya `"healthline.csv"` |
| 1.4 | `Blogs_ACLE` | Scraped blog articles → ACLE video lessons | `"Healthline.csv"` ya `"Healthline"` |
| 1.5 | `Course_New` | Professional Certificate Programs create karta hai | `"AI"` ya `"Programs.csv"` |
| 1.6 | `Course_ACLE` | Course lessons → ACLE video lessons | `"Course_ACLE_Planner.csv"` |
| 1.7 | `Wiki_HIEN` | Wiki articles likhta hai (Hinglish) | `"Browser"` ya `"Articles.csv"` |
| 1.8 | `Wiki_ACLE` | Wiki articles → ACLE video format | `"HIEN.csv"` ya `"HIEN/A/Algorithm"` |
| 1.9 | `Wikipedia_Article` | Wikipedia download + HIEN/HI translate | `"A"` ya `"Albert_Einstein"` |
| 1.10 | `Wikipedia_ACLE` | Wikipedia articles → ACLE video | `"HIEN.csv"` ya `"HIEN"` |
| 1.11 | `Role_HIEN` | Role SOP documents (Hinglish) | `"Software_Engineer"` ya `"Roles.csv"` |
| 1.12 | `Role_ACLE` | Role SOPs → ACLE video format | `"Roles.csv"` ya `"Software_Engineer"` |
| 1.13 | `Skill_ACLE` | Skill lessons → ACLE video format | `"HIEN.csv"` ya `"HIEN"` |
| 1.14 | `Role_EN` | Role SOP documents (English) — *Draft* | `"Software_Engineer"` ya `"Roles.csv"` |
| 1.15 | `Role_HI` | Role SOP documents (Hindi Devanagari) — *Draft* | `"Software_Engineer"` ya `"Roles.csv"` |

### Copy-Paste Samples
```
Workflow("Blog_Article", "AI_Impact_On_Engineers", "AI ke impact pe article likho, beginner friendly tone")
Workflow("Blog_ACLE", "HIEN.csv", "Description : 1 to 100")
Workflow("Blogs_New", "healthline.com", "Healthline ke top articles download karo")
Workflow("Blogs_ACLE", "Healthline.csv", "Description : 1 to 100")
Workflow("Course_New", "AI", "AI Professional Certificate program banao with 7 courses")
Workflow("Course_ACLE", "Course_ACLE_Planner.csv", "Description : 1 to 10")
Workflow("Wiki_HIEN", "Browser", "Web Browser ka ultra detailed wiki article likho")
Workflow("Wiki_ACLE", "HIEN.csv", "Description : 1 to 100")
Workflow("Wikipedia_Article", "A", "A letter ke saare Wikipedia articles download karo")
Workflow("Wikipedia_ACLE", "HIEN.csv", "Description : 1 to 100")
Workflow("Role_HIEN", "Software_Engineer", "Software Engineer ka ultra detailed SOP banao")
Workflow("Role_ACLE", "Roles.csv", "Description : 1 to 10")
Workflow("Skill_ACLE", "HIEN.csv", "Description : 1 to 100")
Workflow("Role_EN", "Software_Engineer", "Software Engineer SOP in English")
Workflow("Role_HI", "Software_Engineer", "Software Engineer SOP Hindi me banao")
```

---

# 2. WebApp

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 2.1 | `WebApp_Screen` | New screens banata hai | `"AppName/ScreenName"` |
| 2.2 | `WebApp_Screen_Update` | Existing screens update (Audit-first) | `"AppName/ScreenName"` |
| 2.3 | `WebApp_Section` | New sections banata hai (Screen sub-parts) | `"AppName/Screen_SectionName"` |
| 2.4 | `WebApp_Section_Update` | Existing sections update | `"AppName/Screen_SectionName"` |
| 2.5 | `WebApp_Component` | New reusable components banata hai | `"AppName/ComponentName"` |
| 2.6 | `WebApp_Component_Update` | Existing components update | `"AppName/ComponentName"` |
| 2.7 | `WebApp_CSS` | App-level CSS generate karta hai | `"AppName"` |
| 2.8 | `WebApp_CSS_Update` | Existing app CSS update | `"AppName"` |
| 2.9 | `WebApp_Layout` | Layout parts (Header/Footer/Nav) | `"AppName/LayoutPart"` |
| 2.10 | `WebApp_Structure` | Initial folder structure setup | `"AppName"` |
| 2.11 | `WebApp_Structure_Update` | Existing structure update | `"AppName"` |
| 2.12 | `WebApp_Update` | High-level app update orchestrator | `"AppName"` |

### Copy-Paste Samples
```
Workflow("WebApp_Screen", "Exchange/Deposit, Exchange/Home", "UI premium hona zaroori hai")
Workflow("WebApp_Screen_Update", "Exchange/Deposit", "Deposit screen me amount validation fix karo")
Workflow("WebApp_Section", "Exchange/Deposit_Header, Exchange/Home_Hero", "Clean UI")
Workflow("WebApp_Section_Update", "Exchange/Deposit_Header", "Header me nav add karo")
Workflow("WebApp_Component", "Exchange/Deposit_Transactions", "UI premium hona zaroori hai")
Workflow("WebApp_Component_Update", "Exchange/Deposit_Transactions", "Pagination add karo")
Workflow("WebApp_CSS", "Exchange", "Blue brand + premium feel")
Workflow("WebApp_CSS_Update", "Exchange", "Dark mode support add karo")
Workflow("WebApp_Layout", "Exchange/Nav, Exchange/Footer", "Premium layout UX")
Workflow("WebApp_Structure", "Exchange", "Initial folder setup karo")
Workflow("WebApp_Structure_Update", "Exchange", "New module folders add karo")
Workflow("WebApp_Update", "Exchange", "Poora app audit karo aur critical bugs fix karo")
```

---

# 3. WebOS Engine

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 3.1 | `WebOS_Engine_PHP` | PHP engines create | `"WebOS.Cache"` |
| 3.2 | `WebOS_Engine_PHP_Update` | PHP engines update (Audit-first) | `"WebOS.Cache"` |
| 3.3 | `WebOS_Engine_JS` | JS engines create | `"WebOS.UI"` |
| 3.4 | `WebOS_Engine_JS_Update` | JS engines update | `"WebOS.UI"` |
| 3.5 | `WebOS_Engine_Bash` | Bash engines create | `"WebOS.Deploy"` |
| 3.6 | `WebOS_Engine_Bash_Update` | Bash engines update | `"WebOS.Deploy"` |
| 3.7 | `WebOS_Engine_SQL` | SQL engines create | `"WebOS.Schema"` |
| 3.8 | `WebOS_Engine_SQL_Update` | SQL engines update | `"WebOS.Schema"` |

### Copy-Paste Samples
```
Workflow("WebOS_Engine_PHP", "WebOS.Cache", "Full caching engine banao with TTL support")
Workflow("WebOS_Engine_PHP_Update", "WebOS.Cache", "TTL handling fix karo aur LRU add karo")
Workflow("WebOS_Engine_JS", "WebOS.UI", "Frontend UI engine banao")
Workflow("WebOS_Engine_JS_Update", "WebOS.UI", "Animation performance improve karo")
Workflow("WebOS_Engine_Bash", "WebOS.Deploy", "Deployment automation engine")
Workflow("WebOS_Engine_SQL", "WebOS.Schema", "Database schema migration engine")
```

---

# 4. WebSDK Module

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 4.1 | `WebSDK_Module` | Complete module structure create | `"ModuleName"` |
| 4.2 | `WebSDK_Module_API` | Module API endpoints generate | `"Module/ApiName"` |
| 4.3 | `WebSDK_Module_API_Update` | Module APIs update (Audit-first) | `"Module/ApiName"` |
| 4.4 | `WebSDK_Module_Class` | Module PHP classes generate | `"Module/ClassName"` |
| 4.5 | `WebSDK_Module_Class_Update` | Module classes update | `"Module/ClassName"` |
| 4.6 | `WebSDK_Module_Component` | Reusable SDK components | `"Module/CompName"` |
| 4.7 | `WebSDK_Module_Cron` | Cron jobs generate | `"Module/CronName"` |
| 4.8 | `WebSDK_Module_JS` | Module JS files | `"Module/JsName"` |
| 4.9 | `WebSDK_Module_Screen` | Module screen-level files | `"Module/ScreenName"` |
| 4.10 | `WebSDK_Module_SQL` | SQL schema/migration files | `"Module/SqlName"` |
| 4.11 | `WebSDK_Module_SQL_Update` | Module SQL files update | `"Module/SqlName"` |
| 4.12 | `WebSDK_Module_Webhook` | Webhook handlers generate | `"Module/WebhookName"` |

### Copy-Paste Samples
```
Workflow("WebSDK_Module", "User", "Complete User module banao")
Workflow("WebSDK_Module_API", "User/Login, User/Register", "Auth APIs banao")
Workflow("WebSDK_Module_API_Update", "User/Login", "Rate limiting add karo")
Workflow("WebSDK_Module_Class", "User/Profile", "Profile management class")
Workflow("WebSDK_Module_Class_Update", "User/Profile", "Avatar upload add karo")
Workflow("WebSDK_Module_Component", "User/ProfileCard", "Reusable profile card")
Workflow("WebSDK_Module_Cron", "User/CleanupExpired", "Expired sessions cleanup cron")
Workflow("WebSDK_Module_JS", "User/Validation", "Client-side form validation")
Workflow("WebSDK_Module_Screen", "User/Settings", "User settings screen")
Workflow("WebSDK_Module_SQL", "User/Schema", "User table schema")
Workflow("WebSDK_Module_SQL_Update", "User/Schema", "Add email_verified column")
Workflow("WebSDK_Module_Webhook", "Payment/Stripe", "Stripe webhook handler")
```

---

# 5. PyApp

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 5.1 | `PyApp_Screen` | Python app screens create | `"AppName/ScreenName"` |
| 5.2 | `PyApp_Screen_Update` | Python app screens update | `"AppName/ScreenName"` |
| 5.3 | `PyApp_Section` | Screen sections create | `"AppName/Screen_Section"` |
| 5.4 | `PyApp_Section_Update` | Screen sections update | `"AppName/Screen_Section"` |
| 5.5 | `PyApp_Component` | Reusable components create | `"AppName/CompName"` |
| 5.6 | `PyApp_Component_Update` | Components update | `"AppName/CompName"` |
| 5.7 | `PyApp_CSS` | App-level CSS/QSS generate | `"AppName"` |
| 5.8 | `PyApp_CSS_Update` | App CSS/QSS update | `"AppName"` |
| 5.9 | `PyApp_Layout` | Layout parts (Header/Footer/Nav) | `"AppName/LayoutPart"` |
| 5.10 | `PyApp_Structure` | Initial folder structure setup | `"AppName"` |
| 5.11 | `PyApp_Structure_Update` | Existing structure update | `"AppName"` |
| 5.12 | `PyApp_Update` | High-level app update orchestrator | `"AppName"` |

### Copy-Paste Samples
```
Workflow("PyApp_Screen", "Exchange/Deposit, Exchange/Home", "UI premium hona zaroori hai")
Workflow("PyApp_Screen_Update", "Exchange/Deposit", "Amount validation fix karo")
Workflow("PyApp_Section", "Exchange/Deposit_Header", "Clean UI header")
Workflow("PyApp_Section_Update", "Exchange/Deposit_Header", "Nav add karo")
Workflow("PyApp_Component", "Exchange/Deposit_Transactions", "Premium UI")
Workflow("PyApp_Component_Update", "Exchange/Deposit_Transactions", "Pagination add karo")
Workflow("PyApp_CSS", "Exchange", "Blue brand + premium feel")
Workflow("PyApp_CSS_Update", "Exchange", "Dark mode support")
Workflow("PyApp_Layout", "Exchange/Nav, Exchange/Footer", "Premium layout UX")
Workflow("PyApp_Structure", "Exchange", "Initial folder setup")
Workflow("PyApp_Update", "Exchange", "Full app audit + bug fixes")
```

---

# 6. PyOS Engine

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 6.1 | `PyOS_Engine_Python` | Python engines create | `"PyOS.Cache"` |
| 6.2 | `PyOS_Engine_Python_Update` | Python engines update (Audit-first) | `"PyOS.Cache"` |
| 6.3 | `PyOS_Engine_JS` | JS engines create | `"PyOS.UI"` |
| 6.4 | `PyOS_Engine_JS_Update` | JS engines update | `"PyOS.UI"` |
| 6.5 | `PyOS_Engine_Bash` | Bash engines create | `"PyOS.Deploy"` |
| 6.6 | `PyOS_Engine_Bash_Update` | Bash engines update | `"PyOS.Deploy"` |
| 6.7 | `PyOS_Engine_SQL` | SQL engines create | `"PyOS.Schema"` |
| 6.8 | `PyOS_Engine_SQL_Update` | SQL engines update | `"PyOS.Schema"` |

### Copy-Paste Samples
```
Workflow("PyOS_Engine_Python", "PyOS.Cache", "Full caching engine with TTL support")
Workflow("PyOS_Engine_Python_Update", "PyOS.Cache", "TTL fix + LRU add karo")
Workflow("PyOS_Engine_JS", "PyOS.UI", "Frontend UI engine banao")
Workflow("PyOS_Engine_Bash", "PyOS.Deploy", "Deployment automation")
Workflow("PyOS_Engine_SQL", "PyOS.Schema", "Database migration engine")
```

---

# 7. PySDK Module

| # | WorkflowId | Purpose | Targets Format |
|---|-----------|---------|----------------|
| 7.1 | `PySDK_Module` | Complete module structure create | `"ModuleName"` |
| 7.2 | `PySDK_Module_API` | Module API endpoints generate | `"Module/ApiName"` |
| 7.3 | `PySDK_Module_API_Update` | Module APIs update | `"Module/ApiName"` |
| 7.4 | `PySDK_Module_Class` | Module Python classes generate | `"Module/ClassName"` |
| 7.5 | `PySDK_Module_Class_Update` | Module classes update | `"Module/ClassName"` |
| 7.6 | `PySDK_Module_Component` | Reusable SDK components | `"Module/CompName"` |
| 7.7 | `PySDK_Module_Cron` | Cron jobs generate | `"Module/CronName"` |
| 7.8 | `PySDK_Module_JS` | Module JS files | `"Module/JsName"` |
| 7.9 | `PySDK_Module_Screen` | Module screen files | `"Module/ScreenName"` |
| 7.10 | `PySDK_Module_SQL` | SQL schema/migration files | `"Module/SqlName"` |
| 7.11 | `PySDK_Module_SQL_Update` | Module SQL update | `"Module/SqlName"` |
| 7.12 | `PySDK_Module_Webhook` | Webhook handlers generate | `"Module/WebhookName"` |

### Copy-Paste Samples
```
Workflow("PySDK_Module", "User", "Complete User module banao")
Workflow("PySDK_Module_API", "User/Login, User/Register", "Auth APIs banao")
Workflow("PySDK_Module_API_Update", "User/Login", "Rate limiting add karo")
Workflow("PySDK_Module_Class", "User/Profile", "Profile management class")
Workflow("PySDK_Module_Component", "User/ProfileCard", "Reusable profile card")
Workflow("PySDK_Module_Cron", "User/CleanupExpired", "Expired sessions cleanup")
Workflow("PySDK_Module_SQL", "User/Schema", "User table schema")
Workflow("PySDK_Module_Webhook", "Payment/Razorpay", "Razorpay webhook handler")
```

---

# 8. Git

| # | WorkflowId | Purpose | Safety |
|---|-----------|---------|--------|
| 8.1 | `Git_Push` | Remote par safely push (pull-before-push mandatory) | `--force` BANNED |
| 8.2 | `Git_Pull` | Remote se safely pull (auto-stash dirty tree) | `--rebase` BANNED |
| 8.3 | `Git_Clone` | Repo clone to `/Aliens/` | Existing folder skip |
| 8.4 | `Git_Stash` | Stash save/restore/list/show/apply/drop | `stash clear` BANNED |

### Copy-Paste Samples
```
Workflow("Git_Push", "Course_ACLE", "Push latest ACLE output")
Workflow("Git_Push", "WebSDK, WebOS", "Push both repos")
Workflow("Git_Pull", "Course_ACLE", "Pull latest changes")
Workflow("Git_Pull", "WebOS, WebSDK", "Sync both repos")
Workflow("Git_Clone", "https://github.com/AliensCompany/WebOS.git", "Clone WebOS repo")
Workflow("Git_Clone", "https://github.com/AliensCompany/WebOS.git | WebOS_Dev", "Clone custom name")
Workflow("Git_Stash", "Course_ACLE", "Stash current changes")
Workflow("Git_Stash", "WebOS", "Pop latest stash — restore work")
Workflow("Git_Stash", "WebSDK", "Apply stash@{2} without dropping")
Workflow("Git_Stash", "Course_ACLE", "List all stashes")
```

---

# 9. Memory

| # | WorkflowId | Purpose | Targets = ScopeKey |
|---|-----------|---------|---------------------|
| 9.1 | `Memory-Write` | High-signal memory entry save (scoped) | `"Global.Governance"` / `"WebApp.Exchange"` |
| 9.2 | `Memory-Read` | Scope ke andar memory entries retrieve | Same ScopeKey |
| 9.3 | `Memory-Index` | Memory scope ka search index rebuild | ScopeKey |
| 9.4 | `Memory-Prune` | Purani entries archive (NoDelete compliant) | ScopeKey |

### Copy-Paste Samples
```
Workflow("Memory-Write", "Global.Governance", "Today's changes summarize karo: planner CSV + schema rules")
Workflow("Memory-Write", "WebApp.Exchange", "Deposit flow root-cause capture karo")
Workflow("Memory-Read", "WebApp.Exchange", "Deposit flow decisions find karo")
Workflow("Memory-Read", "Global.Governance", "Latest governance rules")
Workflow("Memory-Index", "WebApp.Exchange", "Index rebuild karo")
Workflow("Memory-Prune", "WebApp.Exchange", "Archive older than 90 days")
```

---

# 10. System & Utility

| # | WorkflowId | Purpose |
|---|-----------|---------|
| 10.1 | `Report` | Cyborg ke liye BI reports (Daily/Weekly/Monthly/Yearly/Dashboard) |
| 10.2 | `VSCode_Chat` | Purane CPU ki reports padhkar context load karta hai |
| 10.3 | `WorkflowNew` | New HUMAN workflow document (SOP) create karta hai |
| 10.4 | `Cyborg` | Naya machine/computer 6-phase provisioning setup |

### Copy-Paste Samples
```
Workflow("Report", "AC0000", "Generate all missing reports for this CPU")
Workflow("Report", "AC0000", "February 2026 ka monthly report")
Workflow("VSCode_Chat", "/Aliens/Report/Cyborg/C1001", "C1001 ka poora context load karo")
Workflow("WorkflowNew", "WebSDK_Module_Class", "SDK module classes kaise banate hain — workflow banao")
Workflow("Cyborg", "C1094", "Default setup kr do")
Workflow("Cyborg", "C1094", "Default setup kr do, saath me repo: Course, Course_ACLE, Wiki, Role")
```

---

# 11. Common/Shared

| # | WorkflowId | Purpose |
|---|-----------|---------|
| 11.1 | `Workflows` | Planner CSV se rows dispatch karta hai (Universal Planner Runner) |
| 11.2 | `Meta` | Planner CSV meta row validate karta hai (pre-flight check) |
| 11.3 | `Docs` | Cross-ecosystem documentation produce karta hai |
| 11.4 | `BugFix_FromLogs` | Error logs se mechanical safe patches (business logic change FORBIDDEN) |
| 11.5 | `Doctor` | Deep diagnostic — thorough Audit + mechanical fixes only |

### Copy-Paste Samples
```
Workflow("Workflows", "Sheet_Planner_STAGE_1.csv", "Run planner for Sheet")
Workflow("Meta", "", "Planner meta validate karo")
Workflow("Docs", "B-Commerce/README", "Enterprise-grade README likho")
Workflow("BugFix_FromLogs", "Auto", "<paste full error logs here>")
Workflow("Doctor", "Auto", "<paste full error logs here>")
Workflow("Doctor", "Auto:WebSDK", "<paste logs — hint: WebSDK domain>")
```

---

# 12. Rules & References (Not Workflows)

| File | Purpose |
|------|---------|
| `Workflow_Universal.md` | Base rules — manifest, safety, errors (har workflow include karta hai) |
| `Workflow_Plural.md` | Orchestrator rules — target parsing, child dispatch, CSV handling |
| `Workflow_Plural-Update.md` | Update rules — Audit mandatory, backward compatibility |
| `Workflow_Singular.md` | Standalone workflow rules — no child dispatch |
| `ACC.Manifest.md` | Developer manifest schema |
| `ACC.Safety.md` | Safety gates, approval rules, NoDelete |
| `ACC.Output.md` | Output format rules |
| `ACC.Targets.md` | Target parsing grammar |
| `ACC.Paths.md` | Path resolution rules |
| `ACC.Errors.md` | Error codes |
| `ACC.Memory.md` | Memory system rules |
| `ACC.ACLE.md` | ACLE system architecture |
| `ACC.ATLE.md` | ATLE system architecture |

---

# 15. Workflow_Zero (Human Execution Workflows)

| # | WorkflowId | Purpose | Tool |
|---|-----------|---------|------|
| 15.1 | `ACLE_New` | Course MD → ULTRA Premium cinematic HTML video lessons (SVG + TTS audio) | Python |
| 15.2 | `ATLE_New` | Course/Skills/Wiki → Lightweight text-reader shell HTML (runtime MD fetch) | PowerShell |

### Copy-Paste Samples
```
Workflow("ACLE_New", "AI_Developer", "Single program convert karo")
Workflow("ACLE_New", "AI_Developer, Advanced_Data_Analytics", "Multiple programs")
Workflow("ACLE_New", "Course", "Saare programs batch me convert karo")
Workflow("ATLE_New", "Course_ATLE", "Course ke saare ATLE shells banao")
Workflow("ATLE_New", "Skill_ATLE", "Skills ke saare shells banao")
Workflow("ATLE_New", "Course_ATLE, Skill_ATLE, Wiki_ATLE", "Sab batch me")
```

---

# Template-Only (Future — No Active Workflows)

`DartApp` · `DartBrand` · `DartOS` · `DartSDK` · `PyBrand` · `SharpApp` · `SharpBrand` · `SharpOS` · `SharpSDK`

---

# Quick Rules

- **Description mandatory** — empty = fail
- **NoDelete** — koi file/folder delete nahi hoga
- **Quality > Speed** — time limit nahi, perfection zaroori
- **CSV Mode** — 1 row per run, batching forbidden
- **Create workflows** = Planning → Code → Documentation
- **Update workflows** = Audit → Planning → Code → Documentation
- **Git safety** = `--force` / `--rebase` / `reset --hard` permanently banned

---

**Total Workflows: 80+** | **Domains: 15** | **Full Detail:** `Docs/ACC/ACC.Workflows.Guide.md`