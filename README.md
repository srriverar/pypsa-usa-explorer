# ⚡ PyPSA-USA — Interactive Explorer 🇺🇸

**Highly configurable bulk transmission model for the USA — cloned in detail from [`PyPSA/pypsa-usa`](https://github.com/PyPSA/pypsa-usa)**

Live Streamlit app that makes the entire `pypsa-usa` workflow browsable and runnable in the browser — **no `mamba env create` + Snakemake needed**.

> **Clone source:** `git clone https://github.com/PyPSA/pypsa-usa.git` — 487 files, pypsa-eur style, Snakemake 7.32, PyPSA 0.30.2 + HiGHS

🔗 **PyPSA-USA docs:** https://pypsa-usa.readthedocs.io  
🔗 **PyPSA:** https://github.com/PyPSA/PyPSA  
🔗 **pypsa-eur:** https://pypsa-eur.readthedocs.io (workflow inspiration)  
🔗 **pypsa-colombia companion:** `../pypsa-interactive/` (your Colombia app)

---

## 🎯 What this app does — clone in detail

Every file, script and folder of `pypsa-usa` becomes an interactive page:

| Repo part | App tab | What user sees & does |
|---|---|---|
| `/README.md`, `docs/source/*.md/.rst`, `CITATION.cff` | **📖 About** | Real docs rendered + links to readthedocs + citations |
| `workflow/Snakefile` + 7 `rules/*.smk` + 51 `scripts/*.py` | **🔀 Workflow** | DAG graphviz + click a rule → see its `.smk` → see each `scripts/*.py` it calls → run a synthetic mini-step |
| `workflow/config/*.yaml` + `policy_constraints/*.csv` | **⚙️ Config Lab** | View `config.common.yaml` (foresight, renewable, atlite cutouts, lines, snapshots) and tweak `interconnect, clusters, planning_horizons, opts, sector, ll, simpl` → `▶️ Build network from this config` |
| `workflow/repo_data/` (ReEDS, WECC ADS, costs, geospatial) | **📁 Repo Explorer → Data Lab** | Tables of `ReEDS_Constraints/transmission/cost_hurdle`, `WECC_ADS/GeneratorList`, `costs/eia_tech_costs`, `geospatial/BA_shapes` |
| `workflow/envs/` (`environment.yaml`, `dev.yaml`) | **🤝 Contributing → Install** | Exact conda/uv commands to replicate env |
| `.github/workflows/main.yml`, `test.sh`, `.test_sh` | **✅ Validation** | Live `validate.smk` DAG, `test.sh` dry-run, CI micromamba cache + pytest |
| `workflow/scripts/test/` | **✅ Validation → pytest** | `pytest -v` mock with 12 tests (like `test_build.py`, `test_network.py`) |
| **Whole simulations** | **🏗️ CEP 5+1 / 💰 PSC 9+1 / 🔀 PF 9+1** | See below |

---

## 🧪 Three simulation labs — faithful to `pyproject` description

> *“highly configurable power systems model that can be used for **capacity expansion modeling, production cost simulation, and power flow analysis**”*

All labs use **same network builder** `build_usa_network(interconnect, clusters, planning_horizons, opts, sector, foresight, …)` → **PyPSA + HiGHS** in browser. Like `pypsa-usa`: `interconnect ∈ {western, eastern, texas, usa}`, `clusters ∈ {9,20,50,100}`, `opts = Co2L/RPS/copt`, `ll = 1.0|copt`, `simpl`, `sector = E|E-G`.

### 🏗️ Capacity Expansion (CEP) — 5 faithful + 1 open base

| # | Scenario (opts) | Interconnect | Clusters | PH | Faithful to |
|---|---|---|---|---|---|
| 1 | **Reference 2030** `∅` | western | 20 | 2030 | `config.tutorial.yaml` |
| 2 | **RPS 50 %** `RPS` | western | 20 | 2030 | `ReEDS ces_fraction.csv 0.5` |
| 3 | **Carbon −95 %** `Co2L0.05` | usa | 50 | 2030+2050 | Deep-decarb (Co2L0.05) |
| 4 | **Transmission co-opt** `copt` | usa | 50 | 2030 | `transmission_capacity_future_*` expandable |
| 5 | **Limited land** `Co2L0.3 + limited` | western | 20 | 2030 | `renewable_land_access: limited` + CEC screen |
| 6 | **🛠️ Open user base** | *any* | *any* | *any* | You pick all wildcards + capex |

Each shows `p_nom_opt` bar + dispatch + loading — like `solve_network.py` with `p_nom_extendable=True`.

### 💰 Production-Cost (PSC, dispatch fixed) — 9 + 1

| # | Scenario | What changes (vs base 2019 WECC 20) |
|---|---|---|
| 1 | Base 2019 | 2019 snap, fixed, no expand (validation) |
| 2 | High gas +60% | `build_fuel_prices: gas_mult 1.6` |
| 3 | Drought hydro −35% | `PHS/hydro CF 0.65` |
| 4 | High solar 4.6 MW/km² | `capacity_per_sqkm: 4.6` |
| 5 | High load +15% | `build_demand: load_mult 1.15` |
| 6 | Eastern 50 | eastern, 50 clusters (PJM) |
| 7 | Storage mandate RPS | `storage_mandates.csv` |
| 8 | Offshore 30by30 | `offshore_req_30by30.csv 30 GW` |
| 9 | Carbon tax Co2L0.5 | `co2_tax.csv` |
| 10 | **🛠️ Open base** | You pick interconnect, clusters, year, gas/hydro/load multipliers |

Fixed capacities, `p_nom_extendable=False` → LOPF dispatch only (like `solve_network` production-cost).

### 🔀 Power-Flow (PF) — 9 + 1

| # | Scenario | Physics |
|---|---|---|
| 1 | DC base | `n.lpf()` — what OPF uses |
| 2 | AC base | `n.pf()` Newton-Raphson |
| 3 | N-1 line trip | Trip biggest 230 kV (flowgates NARIS2024) |
| 4 | High renew curtail | Wind 80 % CF |
| 5 | Peak load 1.4× | 3 pm summer |
| 6 | Light load 0.55× | 3 am spring |
| 7 | SCOPF (N-1 secure) | 2 contingencies |
| 8 | 50 vs 20 clusters | Spatial resolution |
| 9 | USA split (3 inter) | WECC+Eastern+Texas separately |
| 10 | **🛠️ Open base** | You pick AC/DC, N-1, load |

Shows `v_mag_pu`, `v_ang`, `p0` + map — like `validate: flowgates`.

All three labs have a **📌 Preset** tab (click ▶️) and **🛠️ Open base** tab (fully configurable, stays yours). The open base is what you keep for your paper/thesis.

---

## ✅ Validation — each check in the repo, live

| Check | File | App shows |
|---|---|---|
| `solve_network_validation` (operations) | `workflow/rules/validate.smk` | 10 `FIGURES_VALIDATE` (`daily_stacked_comparison`, `val_bar_state_emissions`, `val_box_region_lmps`, `val_map_load_shedding`…) → live simulate 24h HiGHS + table Demand vs EIA 0.8% |
| `test.sh` + `workflow/scripts/test/*.py` | `.test_sh`, `test.sh`, `scripts/test/` | List 12 tests + `▶️ Run pytest -v (lightweight)` mock |
| CI `main.yml` | `.github/workflows/main.yml` | Full YAML + cache `data/cutouts` by WEEK + `test.sh` + artifacts `resources/results` → `▶️ Simulate CI` |
| Sample figures | `plot_validation_production.py` | `▶️ Generate sample figures` → dispatch + loading + map |

Run them from **✅ Validation** tab — no clone needed.

---

## 🤝 Contributing — strong continuation (verbatim guide)

The app follows the **Contributing guide you quoted** step-by-step, with interactive checklist:

1. **Submit an Issue** — issue tracker + closed issues tip + minimal repro (OS, Python, steps)
2. **Fork** — `git clone https://github.com/<you>/pypsa-usa.git`
3. **Install dev deps** — `uv pip install -r pyproject.toml --extra dev` **or** `conda env update --file workflow/envs/dev.yaml`
4. **pre-commit** — `pre-commit install` (ruff)
5. **Implement** — `git checkout -b issue-###` never main, docstrings, `git add/commit/push`
6. **Run Tests** — `pytest -v`
7. **PR to `develop`** — `git push -u origin my-feature` → Create PR `your_git/issue-xxx → PyPSA/PyPSA-USA:develop`

Plus **Docs**: Sphinx + MyST → `cd docs && make html && python3 -m http.server --directory 'docs/build/html'` (http://localhost:8000)

Tick the 7 checkboxes → progress bar → 🎉 balloons → link to `Compare` on GitHub. Your next PR could be a new CE scenario (IRA 2030) or NREL exclusion.

---

## 🚀 Run locally

```bash
pip install streamlit plotly pypsa highspy pandas  # xarray==2024.10.0 for cloud
git clone https://github.com/PyPSA/pypsa-usa.git  # needed as subdir pypsa-usa/
streamlit run app.py  # http://localhost:8501
# Test
python tools/test_app.py  # APPTEST OK — 9 tabs, 0 exceptions, 13 buttons
```

> The app isolates the heavy `pypsa-usa` env (atlite, cartopy, geopandas, snakemake) — demos run with **synthetic WECC-like 9/20/50-bus** networks so no 10 GB cutouts needed. For full 500-bus + ERA5, follow `docs/source/about-install.md` inside the app's **📖 About**.

---

## 📂 Structure you asked to clone in detail

```
pypsa-usa/
├── Snakefile (wildcards interconnect/simpl/clusters/ll/opts/sector, 7 rule includes)
├── pyproject.toml (pypsa==0.30.2, atlite 0.3.0, highspy, snakemake 7.32…)
├── workflow/
│   ├── config/ (config.common.yaml, cluster.yaml, plotting.yaml, api.yaml, sector.yaml, policy_constraints/ReEDS csvs)
│   ├── rules/ (common, retrieve, build_electricity, build_sector, solve_electricity, postprocess, validate)
│   ├── scripts/ (51 .py: build_base_network, cluster_network, add_electricity, solve_network, plot_*, summary…)
│   ├── envs/ (environment.yaml, dev.yaml)
│   ├── repo_data/ (ReEDS_Constraints, WECC_ADS, costs, geospatial BA_shapes, NERC, BOEM…)
│   └── notebooks/ (cutouts, docs/validation)
├── docs/source/ (Sphinx, MyST — 25 files)
└── .github/workflows/main.yml (CI micromamba)
```

Every one of those is a clickable file in **📁 Repo Explorer**.

---

## 📄 License & Citation

MIT — see `pypsa-usa/LICENSE.md` + `CITATION.cff` (Zenodo DOI 10.5281/zenodo.10815964). This explorer is companion to `pypsa-colombia` (LICA_SE).

*Highly configurable = you pick interconnect, clusters, ll, opts, sector, planning_horizons, foresight, renewable … we build and solve live.*
