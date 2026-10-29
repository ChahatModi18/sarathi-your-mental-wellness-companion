# 🚀 Deployment Guide: GitHub & Vercel — Sarathi Platform
## *Sarathi: Your Mental Wellness Companion [Research Based Project]*

> **Target Repository Name:** `sarathi-your-mental-wellness-companion`  
> **Repository Title:** *Sarathi: Your Mental Wellness Companion [Research Based Project]*  
> **Target Vercel Project Name:** `sarathi-your-mental-wellness-companion`  
> **Platform Stack:** Flask 3.1 + FastAPI Microservice + NumPy/PyTorch ML + MySQL + Vercel Serverless Python

---

## 🌟 Live Deployed Links

| Resource | Direct Link | Status |
| :--- | :--- | :--- |
| **GitHub Repository** | [https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion](https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion) | ✅ Published & Synchronized (Branch: `main`) |
| **Vercel Production Domain** | [https://sarathi-your-mental-wellness-compan.vercel.app](https://sarathi-your-mental-wellness-compan.vercel.app) | ✅ Live & Operational (HTTP 200 OK) |
| **Vercel Unique Deployment** | [https://sarathi-your-mental-wellness-companion-3xv8j6ust.vercel.app](https://sarathi-your-mental-wellness-companion-3xv8j6ust.vercel.app) | ✅ Deployed (`readyState: READY`) |
| **Vercel Inspection Console** | [https://vercel.com/chahatmodi18s-projects/sarathi-your-mental-wellness-companion/H8npvgSsTDoqRpaHCdCndSNHyWEj](https://vercel.com/chahatmodi18s-projects/sarathi-your-mental-wellness-companion/H8npvgSsTDoqRpaHCdCndSNHyWEj) | ✅ Monitored |

---

## 1. GitHub Deployment Workflow (Repository Creation & Push)

The following tabular sequence guides you through sanitizing, committing, and publishing the research codebase to GitHub without exposing sensitive credentials, environment files, or unnecessary binary blobs.

| Step # | Command / Action | Purpose & Function | Verification & Expected Output |
| :---: | :--- | :--- | :--- |
| **1.1** | `git status` | Audits the current git working tree to inspect modified, untracked, or staged files. | Confirms modified files and verifies ignored folders do not appear. |
| **1.2** | Verify `.gitignore` security rules | Confirms that sensitive files (`.env`, `*.log`, credentials, `archive/`, `food_ordering_platform/`) are shielded from tracking. | `.gitignore` contains rules for `.env`, `*.key`, `*.pem`, `__pycache__`, etc. |
| **1.3** | `git add .` | Stages all sanitized, production-ready project files (templates, backend services, tests, docs, assets). | Running `git status` shows staged changes in green. |
| **1.4** | `git commit -m "feat: release Sarathi mental wellness platform with advanced period diagnostics & tri-theme engine"` | Creates a cryptographic snapshot of the project with a clean, semantic commit message. | `[master (root-commit)] ... 157 files changed...` |
| **1.5** | `git branch -M main` | Renames the default primary branch to `main` conforming to modern GitHub industry standards. | Branch identifier switches from `master` to `main`. |
| **1.6** | **Option A (GitHub API / Automated):**<br>`POST https://api.github.com/user/repos`<br>`{"name": "sarathi-your-mental-wellness-companion", "description": "Sarathi: Your mental Wellness Companion [research based project]", "private": false}` | Automatically initializes the remote repository on the authenticated GitHub user profile. | Returns repository metadata: `https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion`. |
| **1.6** | **Option B (GitHub Web):**<br>1. Open [github.com/new](https://github.com/new)<br>2. Repo name: `sarathi-your-mental-wellness-companion`<br>3. Description: `Sarathi: Your Mental Wellness Companion [Research Based Project]`<br>4. Click **Create repository** | Manual web-based repository initialization for users without automated tokens. | GitHub presents empty repository remote push instructions. |
| **1.7** | `git remote set-url origin https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion.git` | Links your local repository to the new remote GitHub repository. | `git remote -v` outputs the new fetch and push URLs. |
| **1.8** | `git push -u origin main` | Transmits all local commits, branches, and documentation to GitHub. | Output: `To https://github.com/ChahatModi18/... * [new branch] main -> main`. |

---

## 2. Vercel Deployment Workflow (CLI & Git Integration)

Vercel provides edge serverless execution using `@vercel/python` defined in [`vercel.json`](vercel.json). Deploying through the connected GitHub repository enables automated continuous integration (CI/CD) on every future commit.

| Step # | Command / Action | Purpose & Function | Verification & Expected Output |
| :---: | :--- | :--- | :--- |
| **2.1** | Verify `vercel.json` | Confirms routing rules routing all requests to `app.py` with static asset caching. | Root directory contains valid `vercel.json` with `@vercel/python`. |
| **2.2** | Verify `requirements.txt` | Ensures serverless Python dependencies (Flask, TextBlob, NumPy, MySQL Connector) are defined without heavy desktop C-libraries. | `requirements.txt` contains clean web packages; desktop GUI packages reside in `requirements-desktop.txt`. |
| **2.3** | `npx vercel login` | Authenticates your local terminal with your Vercel account via web browser or email code. | `Success! Email confirmed` / logged in as `chahatmodi18`. |
| **2.4** | `npx vercel link` | Links your local directory to a Vercel project named `sarathi-your-mental-wellness-companion`. | Project metadata saved in `.vercel/project.json`. |
| **2.5** | Configure Environment Variables:<br>`npx vercel env add FLASK_SECRET_KEY production`<br>`npx vercel env add DB_HOST production`<br>`npx vercel env add DB_USER production`<br>`npx vercel env add DB_PASSWORD production`<br>`npx vercel env add DB_NAME production` | Securely injects production secrets and cloud MySQL database credentials into the Vercel serverless environment. | Secret stored encrypted in Vercel Cloud KMS without appearing in code or git history. |
| **2.6** | `npx vercel deploy --prod --yes` | Packages and deploys the clean serverless web bundle to Vercel production edge servers. | Returns production URL: `https://sarathi-your-mental-wellness-compan.vercel.app`. |
| **2.7** | Verify Live Health Check | Probes the live HTTP endpoint to ensure WSGI handlers and Jinja templates render properly. | HTTP 200 OK response with full rendered HTML. |

---

## 3. Alternative: One-Click Vercel Web Dashboard Deployment

If you prefer deploying via the Vercel Graphical Web UI:

| Step # | Web UI Action | Purpose & Details |
| :---: | :--- | :--- |
| **3.1** | Open [vercel.com/new](https://vercel.com/new) | Access the Vercel project creation portal. |
| **3.2** | Select **Import Git Repository** | Connects to `ChahatModi18/sarathi-your-mental-wellness-companion`. |
| **3.3** | Set Project Name to `sarathi-your-mental-wellness-companion` | Ensures brand and project naming consistency across GitHub and Vercel. |
| **3.4** | Framework Preset: **Other** | Vercel automatically detects `@vercel/python` from `vercel.json`. |
| **3.5** | Expand **Environment Variables** | Provide `FLASK_SECRET_KEY`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`. |
| **3.6** | Click **Deploy** | Initiates automated cloud build, dependency installation, and domain routing. |

---

## 4. Security & Sanitization Checklist

- [x] `.env` excluded via `.gitignore` and `.vercelignore`
- [x] No plaintext passwords or database credentials committed
- [x] Non-web assets and large binaries excluded from serverless bundle
- [x] Offline fallback active (NumPy neural models run if PyTorch/CUDA omitted)
- [x] 58/58 unit and integration tests passing locally before deployment
- [x] Voicebot strictly route-scoped (never renders on `/login` or `/register`)
- [x] Tri-theme accessibility contrast tokens preserved across all viewports
