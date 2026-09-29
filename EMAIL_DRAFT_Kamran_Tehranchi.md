# Email draft — Proof of Concept to Kamran Tehranchi (ktehranchi@stanford.edu)

> Copy-paste into Gmail/Outlook. Subject line, body, and signature are ready. Customize the bracketed parts if you want.

---

**Subject:** Proof of Concept — PyPSA-USA Interactive Explorer (Streamlit) — proposal to collaborate | PyPSA Workshop Berlin Oct 14

**To:** ktehranchi@stanford.edu
**Cc:** (optional) — your group / LICA_SE

---

Dear Dr. Tehranchi,

I hope you are well. I am **Prof. Sergio Rivera** — **LICA_SE** (Laboratorio de Investigación en Conversión y Almacenamiento de Energía) and **EMC-UN** group, **Universidad Nacional de Colombia** — currently on **sabbatical**.

I am writing following your **Contributing** note:

> *We welcome your contributions to this project. Please see the [contributions](https://pypsa-usa.readthedocs.io/en/latest/contributing.html) guide in our readthedocs page for more information. Please do not hesitate to reach out to ktehranchi@stanford.edu with specific questions, requests, or feature ideas.*

I have built a **proof-of-concept interactive explorer for PyPSA-USA** that I would love to continue developing **with you and the PyPSA-USA team**, if you find it useful.

**What it is (2 min to try):**

* **Live Streamlit app** that clones `PyPSA/pypsa-usa` **in detail** — every file/folder (`Snakefile`, 7 `workflow/rules/*.smk`, 51 `workflow/scripts/*.py`, `workflow/config/*.yaml` + `repo_data/ReEDS`, `docs`, `.github/workflows/main.yml`) becomes browsable inside the app. No `mamba env create` / `snakemake` needed to explore.
* Three faithful simulation labs running **PyPSA + HiGHS** in the browser on **synthetic but faithful WECC/Eastern/Texas/USA networks** — exactly the wildcards from `config.common.yaml` + `Snakefile`: `interconnect, simpl, clusters, ll, opts, sector, planning_horizons, foresight, renewable`:
  * **🔀 Power-Flow 9+1** (DC LPF / AC Newton-Raphson, N-1, SCOPF) — now **first tab** as physics-first
  * **💰 Production-Cost 9+1** (fixed capacities, dispatch only)
  * **🏗️ Capacity Expansion 5+1** (ReEDS `Co2L`, `RPS/ces_fraction`, `copt` transmission, limited land — plus a fully **open user base** you keep for a paper/thesis)
* **Highly configurable + understandable:** size is now **unmistakable** → top of **Config Lab**: `🌎 Interconnect (western/eastern/texas/usa)` × `🔢 Clusters (4 → 300)` with spectrum `4 tiny → 20 tutorial → 50 research → 100 planning → 200 very large`, `👁️ Preview SIZE on USA map`, and KPIs after every run (`Demand vs Dispatched`, `Renewable share`, `v_mag`, `Max line %`). The **intensive USA map** is used for every result (buses sized = capacity+load, lines colored `>85% congested`).
* **Validated like the repo:** `workflow/rules/validate.smk` (10 `FIGURES_VALIDATE`), `test.sh` + `pytest -v`, and `.github/workflows/main.yml` CI — all shown live with `▶️ Simulate` buttons.
* **Contributing verbatim:** the 6-step guide + `uv`/`mamba dev`, `pre-commit`, `pytest -v`, PR to `develop`, and `cd docs && make html` (Sphinx + MyST) — with an interactive checklist.

**Why I built it:** as a companion to our **PyPSA-Colombia** explorer (`pypsacolombia`, same idea for Colombia's SIN) and to lower the entry barrier for students and planners — while staying **100 % faithful** to your workflow, costs, and geospatial data. Code is **MIT**, ready for Streamlit Cloud.

**Links (proof of concept):**

* **GitHub (ready to push):** `[paste your new repo URL here — e.g., https://github.com/srriverar/pypsa-usa-explorer]` — I will push the enclosed `.zip` (`pypsa-usa-app` — `app.py` 1169 lines, `requirements.txt`, `pypsa-usa/` clone, `README.md`) today and deploy to Streamlit.
* **Live demo (temporary Arena):** `[paste your current preview URL — e.g., https://8504-....e2b.app]` — runs without installation.
* **Zip attached:** `pypsa-usa-app.zip` (8.8 MB, `.git` excluded) — unzip → `pip install -r requirements.txt` → `streamlit run app.py`

**My context & availability:**

* I am on **sabbatical**, will be at the **PyPSA Workshop in Berlin — October 14**, and next week at **Stanford for the AI Leadership course**. I would be delighted to meet in Berlin or (if convenient) at Stanford to discuss next steps, get your feedback, and align the app with your roadmap.
* My group **LICA_SE / EMC-UN** (https://github.com/srriverar/LICA_SE · https://licase.streamlit.app — GIS dashboard) works on WGA-style scaffolding for country explorers; this USA app is the template we hope to co-develop with you.

**How I would love to collaborate (if you are interested):**

1. **You review the PoC** — does this faithfully represent the workflow and validation you intend? Any wildcards/constraints I missed?
2. We **open 1–2 issues** on `PyPSA/pypsa-usa` → I implement via your 6-step flow (branch `issue-###` → `pre-commit` → `pytest -v` → PR to `develop`) — e.g., a new CEP scenario (IRA 2030), extra validation figure, or docs tweak.
3. We **co-decide where the explorer should live** — as a separate `pypsa-usa-explorer` repo under my group with your guidance, or as `docs`-linked gallery / companion — whatever you prefer. I will maintain it and keep it synced with `master`.

If this is of interest, I can **push to GitHub today** and share the Streamlit URL, and we can schedule a **20-min call** before Berlin (I am flexible next week at Stanford).

Thank you for PyPSA-USA and for the invitation to reach out — and for considering this collaboration. I appreciate any feedback, even brief.

Warm regards,

**Prof. Sergio Rivera, Ph.D.**
LICA_SE — EMC-UN — Universidad Nacional de Colombia
GitHub: https://github.com/srriverar/LICA_SE
LICA_SE App: https://licase.streamlit.app
[phone] | [personal page if any]
Sabbatical 2026 — PyPSA WS Berlin Oct 14 · Stanford AI Leadership [next week dates]

**P.S.** Zip and README are attached; `app.py` is intentionally synthetic (9–300 buses) to run on Streamlit without 10 GB Atlite cutouts — full 500-bus + ERA5 follows your `docs/source/about-install.md`, linked inside the app's **📖 About**.

---

## Short version (if you prefer a 1-paragraph outreach)

> Dear Dr. Tehranchi, I am Prof. Sergio Rivera (UNAL, LICA_SE/EMC-UN, on sabbatical, at PyPSA Berlin Oct 14 and Stanford AI Leadership next week). Following your Contributing note (ktehranchi@stanford.edu), I built a Streamlit proof-of-concept that clones PyPSA-USA in detail (Snakefile/rules/scripts/config/validate/CI) and lets users run Power-Flow → Production-Cost → Capacity Expansion (9+1/9+1/5+1 + open bases) with PyPSA+HiGHS on WECC/Eastern/Texas/USA 4→300 buses, with intensive USA maps. May I share the GitHub/Streamlit PoC for your feedback and explore collaborating via your 6-step guide? Thank you. — Sergio

---

## Checklist before sending

- [ ] Attach `pypsa-usa-app.zip` (8.8 MB)
- [ ] Replace `[paste your new repo URL]` and `[preview URL]` after you push/deploy
- [ ] Adjust Stanford week dates and Berlin session if needed
- [ ] Add phone/signature details
