# 🚀 Deployment Guide: GitHub & Vercel — Sarathi Platform
## *Sarathi: Your Mental Wellness Companion [Research Based Project]*

> **Target Repository Name:** `sarathi-your-mental-wellness-companion`  
> **Repository Title:** *Sarathi: Your Mental Wellness Companion [Research Based Project]*  
> **Target Vercel Project Name:** `sarathi-your-mental-wellness-companion`  
> **Platform Stack:** Flask 3.1 + FastAPI Microservice + NumPy/PyTorch ML + MySQL + Vercel Serverless Python

---

## 1. GitHub Deployment Workflow (Repository Creation & Push)

The following tabular sequence guides you through sanitizing, committing, and publishing the research codebase to GitHub without exposing sensitive credentials, environment files, or unnecessary binary blobs.

| Step # | Command / Action | Purpose & Function | Verification & Expected Output |
| :---: | :--- | :--- | :--- |
| **1.1** | `git status` | Audits the current git working tree to inspect modified, untracked, or staged files. | Confirms modified files and verifies ignored folders do not appear. |
| **1.2** | Verify `.gitignore` security rules | Confirms that sensitive files (`.env`, `*.log`, credentials, `archive/`, `food_ordering_platform/`) are shielded from tracking. | `.gitignore` contains rules for `.env`, `*.key`, `*.pem`, `__pycache__`, etc. |
| **1.3** | `git add .` | Stages all sanitized, production-ready project files (templates, backend services, tests, docs, assets). | Running `git status` shows staged changes in green. |
| **1.4** | `git commit -m "feat: release Sarathi mental wellness platform with advanced period diagnostics & tri-theme engine"` | Creates a cryptographic snapshot of the project with a clean, semantic commit message. | `[master (root-commit)] ... 58 files changed...` |
| **1.5** | `git branch -M main` | Renames the default primary branch to `main` conforming to modern GitHub industry standards. | Branch identifier switches from `master` to `main`. |
| **1.6** | **Option A (GitHub CLI):**<br>`gh repo create sarathi-your-mental-wellness-companion --public --source=. --remote=origin --description="Sarathi: Your Mental Wellness Companion [Research Based Project]"` | Automatically creates the remote repository on your GitHub account and sets `origin` in a single command. | Returns GitHub repository URL: `https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion`. |
| **1.6** | **Option B (GitHub Web):**<br>1. Open [github.com/new](https://github.com/new)<br>2. Repo name: `sarathi-your-mental-wellness-companion`<br>3. Description: `Sarathi: Your Mental Wellness Companion [Research Based Project]`<br>4. Click **Create repository** | Manual web-based repository initialization for users without `gh` CLI installed. | GitHub presents empty repository remote push instructions. |
| **1.7** | `git remote set-url origin https://github.com/ChahatModi18/sarathi-your-mental-wellness-companion.git` | Links your local repository to the new remote GitHub repository. | `git remote -v` outputs the new fetch and push URLs. |
| **1.8** | `git push -u origin main` | Transmits all local commits, branches, and documentation to GitHub. | Output: `To https://github.com/ChahatModi18/... * [new branch] main -> main`. |

---

## 2. Vercel Deployment Workflow (CLI & Git Integration)

Vercel provides edge serverless execution using `@vercel/python` defined in [`vercel.json`](vercel.json). Deploying through the connected GitHub repository enables automated continuous integration (CI/CD) on every future commit.

| Step # | Command / Action | Purpose & Function | Verification & Expected Output |
| :---: | :--- | :--- | :--- |
| **2.1** | Verify `vercel.json` | Confirms routing rules routing all requests to `app.py` with static asset caching. | Root directory contains valid `vercel.json` with `@vercel/python`. |
| **2.2** | Verify `requirements.txt` | Ensures serverless Python dependencies (Flask, TextBlob, NumPy, MySQL Connector) are defined without heavy desktop C-libraries. | `requirements.txt` contains clean web packages; desktop GUI packages reside in `requirements-desktop.txt`. |
| **2.3** | `npx vercel login` | Authenticates your local terminal with your Vercel account via web browser or email code. | `Success! Email confirmed` / logged in as your Vercel user handle. |
| **2.4** | `npx vercel link` | Links your local directory to a Vercel project named `sarathi-your-mental-wellness-companion`. | Prompts: *Set up “sarathi-your-mental-wellness-companion”? [Y/n]* &rarr; selects your team/account. |
| **2.5** | Configure Environment Variables:<br>`npx vercel env add FLASK_SECRET_KEY production`<br>`npx vercel env add DB_HOST production`<br>`npx vercel env add DB_USER production`<br>`npx vercel env add DB_PASSWORD production`<br>`npx vercel env add DB_NAME production` | Securely injects production secrets and cloud MySQL database credentials into the Vercel serverless environment. | Secret stored encrypted in Vercel Cloud KMS without appearing in code or git history. |
| **2.6** | `npx vercel` | Triggers a Preview Deployment to test builds, routing, and asset serving on an isolated Vercel preview URL. | Returns preview deployment URL: `https://sarathi-your-mental-wellness-companion-xxx.vercel.app`. |
| **2.7** | `npx vercel --prod` | Deploys the production release and assigns the canonical project domain. | Returns production URL: `https://sarathi-your-mental-wellness-companion.vercel.app`. |

---

## 3. Alternative: One-Click Vercel Web Dashboard Deployment

If you prefer deploying via the Vercel Graphical Web UI:

| Step # | Web UI Action | Purpose & Details |
| :---: | :--- | :--- |
| **3.1** | Navigate to [vercel.com/new](https://vercel.com/new) | Opens the Vercel Import Git Repository screen. |
| **3.2** | Select **Import** next to `sarathi-your-mental-wellness-companion` | Connects Vercel's continuous delivery pipeline to your GitHub repository. |
| **3.3** | Project Name: `sarathi-your-mental-wellness-companion` | Sets the project name matching your GitHub repository. |
| **3.4** | Framework Preset: **Other** (Root directory: `./`) | Vercel automatically detects `vercel.json` and configures the `@vercel/python` builder. |
| **3.5** | **Environment Variables**: Add your cloud database credentials: <br>• `FLASK_SECRET_KEY`: `sarathi_secret_prod_key_#$99` <br>• `DB_HOST`: Your cloud database host (e.g. PlanetScale / Aiven / TiDB) <br>• `DB_USER`: Database username <br>• `DB_PASSWORD`: Database password <br>• `DB_NAME`: `sarathi_sih_db` | Injects runtime environment secrets without committing them to git. |
| **3.6** | Click **Deploy** | Vercel builds the container, installs `requirements.txt`, optimizes assets, and assigns your live URL (`https://sarathi-your-mental-wellness-companion.vercel.app`). |

---

## 4. Production Environment Variables Reference

| Environment Variable | Required | Default / Fallback | Description |
| :--- | :---: | :--- | :--- |
| `FLASK_SECRET_KEY` | Recommended | `sarathi_secret_1294_#$!` | Cryptographic session cookie signature key. |
| `DB_HOST` | Production | `localhost` | Cloud MySQL host address (e.g., PlanetScale / AWS RDS / TiDB). |
| `DB_USER` | Production | `root` | MySQL database user. |
| `DB_PASSWORD` | Production | `chahat` | MySQL database password. |
| `DB_NAME` | Production | `sarathi_sih_db` | Target database catalog name. |
| `OPENAI_API_KEY` | Optional | `None` (Local Neural Fallback) | Optional GPT-3.5/GPT-4 key; if omitted, pipeline uses local He-initialized neural networks. |
| `PYTHON_VERSION` | Optional | `3.11` | Serverless Python runtime environment version. |

---

## 5. Security & Sensitive File Audit Verification

Before pushing to GitHub, verify that your repository does NOT track sensitive assets:

```powershell
# 1. Audit files staged for commit:
git status

# 2. Verify that no .env or sensitive files appear in git tracking:
git ls-files | findstr "\.env"
git ls-files | findstr "password"
git ls-files | findstr "\.pem"

# 3. Confirm only production-safe files are tracked:
git ls-files
```

> [!NOTE]
> All local development databases, `.log` files, virtual environment folders (`Lib/`, `Scripts/`), and personal notes remain safe on your local disk and will never be pushed to GitHub due to `.gitignore` exclusions.
