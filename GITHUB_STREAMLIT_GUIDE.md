# Push to GitHub + Deploy to Streamlit — 5 minutes

This is the `pypsa-usa-app.zip` you will send to Kamran and deploy yourself.

## 1) Unzip locally
```bash
unzip pypsa-usa-app.zip
cd pypsa-usa-app
ls  # app.py  requirements.txt  README.md  pypsa-usa/  assets/  tools/
```

## 2) Create a new GitHub repo
1. Go to https://github.com/new
   - **Name:** `pypsa-usa-explorer` (or `pypsa-usa-interactive`)
   - **Visibility:** Public (needed for Streamlit Community Cloud free tier)
   - **Do not** initialize with README/.gitignore (you already have them)
2. Copy the remote URL, e.g. `https://github.com/srriverar/pypsa-usa-explorer.git`

## 3) Push
```bash
cd pypsa-usa-app
git init
git add app.py requirements.txt README.md assets backup GITHUB_STREAMLIT_GUIDE.md EMAIL_DRAFT_Kamran_Tehranchi.md
git add pypsa-usa  # optional: you can also add as submodule instead
# .git is excluded from zip — fresh init is correct
git commit -m "feat: PyPSA-USA Interactive Explorer PoC — PF 9+1 PSC 9+1 CEP 5+1, intensive USA map, size 4->300"

# If you keep pypsa-usa as subfolder (current zip), just push:
git branch -M main
git remote add origin https://github.com/srriverar/pypsa-usa-explorer.git
git push -u origin main

# Alternative (cleaner, recommended for long term): use submodule
# git submodule add https://github.com/PyPSA/pypsa-usa.git pypsa-usa
# git add .gitmodules pypsa-usa
# git commit -m "chore: add pypsa-usa as submodule"
# git push
```

> **Note:** `pypsa-usa/.git` was excluded from the zip (8.8 MB vs 142 MB). The app has a fallback: if `.github/workflows/main.yml` is missing, it shows `assets/main.yml` and tries the raw GitHub URL. No error on Streamlit Cloud. If you push with `git submodule add`, Streamlit will fetch it automatically.

## 4) Deploy to Streamlit Community Cloud
1. Go to https://share.streamlit.io → **New app**
2. **Repository:** `srriverar/pypsa-usa-explorer` · **Branch:** `main` · **Main file path:** `app.py`
3. **Python version:** 3.11 or 3.12 (3.13 also works; we use 3.13 + pypsa 1.3.0)
4. Click **Deploy** — build uses `requirements.txt`:
```
streamlit>=1.32,<2
pandas>=2.2,<3
numpy>=1.24
plotly>=5.18
pypsa==1.3.0
linopy==0.9.1
xarray==2024.10.0
netcdf4>=1.7
highspy>=1.8
scipy>=1.12
```
5. After 2–3 min: copy the URL `https://<your-app>.streamlit.app` — paste it into the email to Kamran (replace `[preview URL]`).

## 5) Local test before pushing (optional)
```bash
pip install -r requirements.txt
streamlit run app.py  # http://localhost:8501
python tools/test_app.py  # APPTEST OK — 0 exceptions
```

## 6) What to send Kamran
- The **GitHub URL** + **Streamlit URL** (once deployed)
- The **zip** as attachment (proof of MIT + offline run)
- The **email draft** from `EMAIL_DRAFT_Kamran_Tehranchi.md`

## 7) After Kamran replies
- Open an Issue on `PyPSA/pypsa-usa` (per contributing.md Step 1)
- Branch `issue-###` → `pre-commit install` → implement → `pytest -v` → PR to `develop` (Step 6)

---

### Streamlit secrets / settings
No secrets needed. The app is synthetic (9–300 buses) and runs **HiGHS** without Gurobi license. For full 500-bus + Atlite cutouts, follow `pypsa-usa/docs/source/about-install.md` (linked in **📖 About**).

### Updating the app
Just `git add app.py && git commit -m "feat: ..." && git push` — Streamlit auto-redeploys.

### Size & performance on Streamlit Cloud
- `4–20` clusters: instant
- `50–100`: 5–15s, works fine on 1 GB RAM
- `200–300`: 30–45s, may hit timeout on free tier — add a note in UI if needed, or limit slider to 100 for cloud and keep 300 for local.
