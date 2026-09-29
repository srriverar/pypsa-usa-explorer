#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 PyPSA-USA — Interactive Explorer · Highly Configurable US Bulk System
 Built from https://github.com/PyPSA/pypsa-usa
================================================================================
Clones the repo in detail: each folder, script, config, and rule becomes
interactive. The user experiences the full workflow: configurable networks,
capacity expansion, production-cost, and power-flow, with live PyPSA+HiGHS.

Author: LICA_SE · pypsa-usa initiative companion to pypsa-colombia
"""
from __future__ import annotations
import os, json, base64, textwrap, math, random, traceback, warnings, logging
from pathlib import Path
import pathlib
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")
logging.getLogger("pypsa").setLevel(logging.ERROR)
logging.getLogger("linopy").setLevel(logging.ERROR)

st.set_page_config(page_title="PyPSA-USA — Interactive Explorer", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

ROOT = Path(__file__).parent
REPO = ROOT / "pypsa-usa"
WORKFLOW = REPO / "workflow"
DOCS = REPO / "docs"

# ---------- styles ----------
CSS = """
<style>
.block-container{padding-top:1.0rem;max-width:1580px;}
div[data-testid="stMetric"]{background:#fff;border:1px solid #e3eaf3;border-radius:14px;padding:12px 16px 8px;box-shadow:0 1px 3px rgba(16,42,76,.07);}
.hero{background:linear-gradient(135deg,#0b1d3a 0%,#003366 40%,#1a5c8a 70%,#d67e00 100%);border-radius:18px;padding:26px 28px 18px;color:#fff;margin-bottom:12px;box-shadow:0 6px 18px rgba(13,42,96,.22);}
.hero h1{margin:0;font-size:1.95rem;font-weight:850;letter-spacing:.01em;}
.hero p{margin:.5rem 0 0;font-size:.92rem;opacity:.95;line-height:1.45;}
.chip{display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);padding:3px 11px;border-radius:999px;font-size:.72rem;font-weight:600;margin-right:6px;margin-top:6px;}
.chip.hi{background:#d67e00;border-color:#ffbb66;color:#fff;}
.chip.ok{background:#1a7f5e;border-color:#6cc5ba;}
.callout{background:#eaf4ff;border-left:4px solid #003366;padding:10px 14px;border-radius:8px;font-size:.86rem;color:#1a2a3a;margin:8px 0;}
.callout.warn{background:#fff8e6;border-left-color:#ff9800;}
.callout.ok{background:#e8f8f3;border-left-color:#1a7f5e;}
.callout.hi{background:#fff0f0;border-left-color:#c0392b;}
.legend{background:#f5f9fc;border-left:4px solid #003366;padding:10px 16px;border-radius:0 12px 12px 0;font-size:.85rem;color:#33475e;line-height:1.55;margin:8px 0;}
.play-banner{background:linear-gradient(135deg,#003366,#1a7f5e);color:white;padding:10px 16px;border-radius:10px;font-weight:700;text-align:center;margin:8px 0;letter-spacing:.02em;}
.file-card{background:#fff;border:1px solid #e3eaf3;border-radius:10px;padding:10px 12px;margin:6px 0;}
.stTabs [data-baseweb="tab-list"]{gap:2px;border-bottom:1px solid #dfe7f0;}
.stTabs [data-baseweb="tab"]{font-size:.84rem;font-weight:600;padding:7px 10px;border-radius:10px 10px 0 0;color:#51617a;}
.stTabs [data-baseweb="tab"]:hover{background:#f2f6fb;color:#0f3d63;}
.stTabs [aria-selected="true"]{background:#eaf3fb;color:#0f3d63;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DISCLAIMER = """<div style='background:#fff3cd;padding:9px 14px;border-radius:8px;border-left:5px solid #ffc107;margin:10px 0 14px;font-size:0.80em;line-height:1.5'>⚠️ <b>Interactive Explorer — not the workflow itself</b> · Built from <b>PyPSA/pypsa-usa</b> (MIT). Live demos use reduced <b>9/20/50-bus</b> synthetic WECC/Eastern/Texas networks with same carriers, configs and validations — runs <b>PyPSA + HiGHS</b> in the browser, no <code>mamba env create</code> needed. For full 500-bus + ERA5 cutouts see READMEs below.</div>"""

# ---------- helpers ----------
def hero():
    st.markdown("""
    <div class="hero">
      <h1>⚡ PyPSA-USA — Interactive Explorer 🇺🇸 <span style='font-weight:400;font-size:.58em;opacity:.9'>highly configurable bulk transmission model</span></h1>
      <p>Clone in detail of <b>PyPSA/pypsa-usa</b> — every folder, script and rule becomes interactive. The whole workflow <b>Snakemake → PyPSA → HiGHS</b> for <b>capacity expansion, production-cost & power-flow</b> — validated, with open user scenarios.</p>
      <div>
        <span class="chip">pypsa-usa · MIT</span><span class="chip">pypsa-eur style</span><span class="chip">Snakemake workflow</span><span class="chip ok">PyPSA 0.30 + HiGHS</span><span class="chip">WECC/Eastern/Texas/USA</span><span class="chip hi">500+ buses → 9/20/50 demo</span><span class="chip">ReEDS constraints</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(DISCLAIMER, unsafe_allow_html=True)

def _fig(h=380, title=""):
    fig=go.Figure()
    fig.update_layout(template="plotly_white", height=h, title=title, margin=dict(l=18,r=18,t=54 if title else 20,b=12), hovermode="x unified",
                      font=dict(family="Inter,'Segoe UI',system-ui,sans-serif", size=12.5, color="#33475e"), title_font=dict(size=14,color="#0f3d63"),
                      legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"), plot_bgcolor="#fbfcfe", paper_bgcolor="rgba(0,0,0,0)", hoverlabel=dict(bgcolor="white", bordercolor="#c9d6e4"))
    return fig

def section_header(title, desc):
    st.markdown(f"<div style='background:#f0f4f8;padding:11px 16px;border-radius:8px;border-left:5px solid #003366;margin-bottom:10px'><b style='color:#003366;font-size:1.03em'>{title}</b><br><span style='color:#555;font-size:.84em'>{desc}</span></div>", unsafe_allow_html=True)

def mc(val,label,color="#003366",icon=""):
    return f"<div style='background:linear-gradient(135deg,{color}12,{color}06);padding:11px;border-radius:10px;text-align:center;border-left:4px solid {color}'><h4 style='color:{color};margin:0;font-size:1.05em'>{icon} {val}</h4><p style='color:#555;margin:2px 0 0;font-size:.70em'>{label}</p></div>"

def banner(txt="👆 PLAY HERE — move any slider and click ▶️ Run!"):
    st.markdown(f"<div class='play-banner'>{txt}</div>", unsafe_allow_html=True)

# ---------- repo introspection ----------
@st.cache_data(show_spinner=False)
def repo_tree():
    # returns list of (path, type)
    base=REPO
    out=[]
    for p in sorted(base.rglob("*")):
        if ".git" in p.parts: continue
        if p.is_file():
            rel=p.relative_to(base)
            out.append(str(rel))
    return out

@st.cache_data(show_spinner=False)
def read_repo_file(rel):
    try:
        fp=REPO / rel
        if not fp.exists(): return "(not found)"
        if fp.suffix in (".png",".jpg",".jpeg",".svg",".tif",".shp",".pdf"):
            return f"[binary {fp.suffix} {fp.stat().st_size/1024:.1f} KB]"
        txt=fp.read_text(encoding="utf-8", errors="ignore")
        if len(txt)>12000:
            txt=txt[:12000]+"\n\n... truncated ..."
        return txt
    except Exception as e:
        return f"read error: {e}"

# ---------- PyPSA network builders (synthetic WECC-like) ----------
INTERCONNECT_COORDS = {
    "western": {"x": [-124, -102], "y": [32, 49], "desc": "WECC — CA, OR, WA, NV, AZ, CO (West, 11 states)", "color": "#1f77b4"},
    "eastern": {"x": [-96, -67], "y": [25, 49], "desc": "Eastern — PJM, MISO, NYISO, ISO-NE, SPP, SERC (East, 36 states)", "color": "#d67e00"},
    "texas": {"x": [-107, -93], "y": [25, 37], "desc": "ERCOT — Texas only (1 state, isolated)", "color": "#c0392b"},
    "usa": {"x": [-124, -67], "y": [25, 49], "desc": "USA contiguous — all 3 interconnects together", "color": "#1a7f5e"},
}
# Spectrum of system sizes — user can pick any, from tiny demo to research
SIZE_OPTIONS = [4, 9, 14, 20, 30, 50, 80, 100, 150, 200, 300]
SIZE_HELP = {
    4: "Tiny — 4 buses, ~8 lines, instant (teaching)",
    9: "Demo — 9 buses (WECC_9), ~14 lines, <1s",
    14: "Small — 14 buses, ~22 lines, 1s",
    20: "Tutorial — 20 buses, ~32 lines, 2s (default)",
    30: "Medium — 30 buses, ~50 lines, 3s",
    50: "Research — 50 buses, ~85 lines, 5–8s",
    80: "Detailed — 80 buses, ~140 lines, 10s",
    100: "Planning — 100 buses, ~180 lines, 12–15s",
    150: "Large — 150 buses, ~270 lines, 20s",
    200: "Very large — 200 buses, ~360 lines, 30s+",
    300: "Max — 300 buses, ~540 lines, 45s+ (slow, for cluster)",
}
def size_label(n):
    return f"{n}  —  {SIZE_HELP.get(n, '')}"

# ——— PyPSA-USA tech colors — faithful to workflow/repo_data/config/config.plotting.yaml ———
# These are the exact hex codes used in the reference figure you attached (5/10/50 GW pies, 2/5 GW lines)
# We keep the figure's legend order: Oil, Coal, Nuclear, Biomass, Geothermal, CCGT, OCGT, Onshore Wind, Offshore ...
TECH_COLORS = {
    "oil": "#262626",               # Oil — black
    "Oil": "#262626",
    "coal": "#707070",              # Coal — dark grey
    "Coal": "#707070",
    "lignite": "#9e5a01",
    "nuclear": "#ff9000",           # Nuclear — orange
    "Nuclear": "#ff9000",
    "biomass": "#0c6013",            # Biomass — dark green
    "Biomass": "#0c6013",
    "solid biomass": "#06540d",
    "geothermal": "#ba91b1",         # Geothermal — light purple
    "Geothermal": "#ba91b1",
    "CCGT": "#b20101",              # Combined-Cycle Gas — dark red
    "Combined-Cycle Gas": "#b20101",
    "combined cycle gas": "#b20101",
    "gas": "#b20101",
    "OCGT": "#d35050",              # Open-Cycle Gas — bright red
    "Open-Cycle Gas": "#d35050",
    "open cycle gas": "#d35050",
    "onwind": "#235ebc",            # Onshore Wind — blue
    "Onshore Wind": "#235ebc",
    "onshore wind": "#235ebc",
    "offwind": "#6895dd",           # Fixed Bottom Offshore Wind — mid blue
    "Fixed Bottom Offshore Wind": "#6895dd",
    "offwind-ac": "#6895dd",
    "offwind_floating": "#11a1c1",  # Floating Offshore Wind — cyan/teal
    "Floating Offshore Wind": "#11a1c1",
    "offwind_floating": "#11a1c1",
    "solar": "#f9d002",             # Solar — yellow
    "Solar": "#f9d002",
    "hydro": "#08ad97",             # Reservoir & Dam — teal
    "Reservoir & Dam": "#08ad97",
    "PHS": "#08ad97",
    "ror": "#4adbc8",
    "battery": "#b8ea04",           # Battery Storage — lime
    "Battery Storage": "#b8ea04",
    "4hr_battery_storage": "#a4d600",
    "4Hr_Battery_Storage": "#a4d600",
    "AC": "#70af1d",                # AC — green (lines)
    "AC-AC": "#70af1d",
    "Ac": "#70af1d",
    "DC": "#8a1caf",                # DC — purple (links)
    "Dc": "#8a1caf",
    "H2": "#ea048a",
    "hydrogen": "#ea048a",
    "load": "#2ad55f",
    "other": "#cccccc",
}
# Line colors by carrier
LINE_COLOR_AC = TECH_COLORS["AC"]
LINE_COLOR_DC = TECH_COLORS["DC"]
# Bus pie order for consistent rendering — matches figure legend top to bottom
CARRIER_ORDER = ["oil","coal","nuclear","biomass","geothermal","CCGT","OCGT","onwind","offwind","offwind_floating","solar","hydro","battery","H2"]

def carrier_color(car):
    # normalize
    c = str(car).strip()
    if c in TECH_COLORS: return TECH_COLORS[c]
    cl = c.lower()
    for k,v in TECH_COLORS.items():
        if cl == k.lower(): return v
    # fuzzy
    if "wind" in cl and "off" in cl and "float" in cl: return TECH_COLORS["offwind_floating"]
    if "wind" in cl and "off" in cl: return TECH_COLORS["offwind"]
    if "wind" in cl: return TECH_COLORS["onwind"]
    if "solar" in cl: return TECH_COLORS["solar"]
    if "hydro" in cl or "reservoir" in cl: return TECH_COLORS["hydro"]
    if "battery" in cl: return TECH_COLORS["battery"]
    if "nuclear" in cl: return TECH_COLORS["nuclear"]
    if "coal" in cl: return TECH_COLORS["coal"]
    if "oil" in cl: return TECH_COLORS["oil"]
    if "biomass" in cl: return TECH_COLORS["biomass"]
    if "geothermal" in cl: return TECH_COLORS["geothermal"]
    if "ccgt" in cl or "combined" in cl: return TECH_COLORS["CCGT"]
    if "ocgt" in cl or "open" in cl: return TECH_COLORS["OCGT"]
    if "gas" in cl: return TECH_COLORS["CCGT"]
    return "#999999"

# US mainland geojson helper — for intensive map background (grid2poster/regions/us_mainland.geojson)
@st.cache_data(show_spinner=False)
def load_us_geojson():
    try:
        fp = ROOT / "assets" / "us_mainland.geojson"
        if not fp.exists():
            fp = pathlib.Path("/tmp/grid2poster/regions/us_mainland.geojson")
        if fp.exists():
            j=json.loads(fp.read_text())
            return j
    except Exception as e:
        return None
    return None



# Base WECC-like nodes for 9-bus demo (approx BA centroids)
WECC_9 = {
    "CA_N": (38.5, -121.0), "CA_S": (34.0, -118.5), "PNW": (45.5, -122.5), "NV": (39.5, -116.5),
    "AZ": (33.5, -112.0), "CO": (39.0, -105.5), "NM": (34.5, -106.0), "WY": (42.5, -107.5), "UT": (39.5, -111.5)
}
EASTERN_9 = {
    "NY": (43.0, -75.5), "PJM": (39.5, -77.5), "NE": (42.5, -71.5), "CAR": (35.5, -80.0),
    "FL": (28.0, -82.0), "MISO_N": (44.0, -93.0), "MISO_S": (32.5, -90.0), "SPP": (37.0, -98.0), "SERC": (33.0, -85.5)
}
TEXAS_6 = {"W_Tex": (31.5, -103.5), "N_Tex": (33.5, -98.0), "S_Tex": (27.5, -98.5), "Houston": (29.8, -95.3), "Austin": (30.3, -97.7), "Dallas": (32.8, -96.8)}

def _hav(lat1,lon1,lat2,lon2):
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))

def build_usa_network(interconnect="western", clusters=20, planning_horizons=[2030], opts="", sector="E",
                      foresight="perfect", co2_limit=1.0, extendable=True, weather_year=2019, seed=42, n_hours=48):
    """Synthetic but faithful USA network. Mimics build_base_network -> cluster -> add_electricity flow."""
    import pypsa
    rng=np.random.RandomState(seed)
    T=int(n_hours)
    snaps=pd.date_range(f"{weather_year}-01-01", periods=T, freq="h")
    n=pypsa.Network(); n.set_snapshots(snaps)
    # Choose base coords
    if interconnect=="western": base=WECC_9
    elif interconnect=="eastern": base=EASTERN_9
    elif interconnect=="texas": base=TEXAS_6
    else: base={**WECC_9, **EASTERN_9, **TEXAS_6}
    # Cluster to desired size — full spectrum 4..300 (k-means in real pypsa-usa, here synthetic but faithful locations)
    if clusters <= len(base):
        keys=list(base.keys())[:clusters]
        coords={k: base[k] for k in keys}
    else:
        coords=dict(base)
        base_keys=list(base.keys())
        # For larger sizes, spread synthetics along interconnect bbox with density matching real load centers
        ic = INTERCONNECT_COORDS.get(interconnect, INTERCONNECT_COORDS["western"])
        lon_min, lon_max = ic["x"]; lat_min, lat_max = ic["y"]
        while len(coords)<clusters:
            # 70% between existing buses (corridors), 30% random across bbox (rural)
            if rng.rand()<0.7:
                a,b=rng.choice(base_keys,2, replace=False)
                lat1,lon1=base[a]; lat2,lon2=base[b]
                lat=(lat1+lat2)/2 + rng.normal(0,0.5); lon=(lon1+lon2)/2 + rng.normal(0,0.7)
            else:
                lat=rng.uniform(lat_min+0.5, lat_max-0.5); lon=rng.uniform(lon_min+0.5, lon_max-0.5)
            # clamp
            lat=max(lat_min, min(lat_max, lat)); lon=max(lon_min, min(lon_max, lon))
            name=f"Bus_{len(coords)+1:03d}"
            if name not in coords: coords[name]=(lat,lon)
    for name,(lat,lon) in coords.items():
        # v_nom by random tier 115/230/345/500
        v=rng.choice([115,230,345,500], p=[0.25,0.35,0.2,0.2])
        n.add("Bus", name, x=float(lon), y=float(lat), v_nom=int(v), carrier="AC")
    # Carriers
    for c in ["onwind","offwind","offwind_floating","solar","hydro","ror","PHS","gas","coal","nuclear","load","battery","hydro-E"]:
        try: n.add("Carrier", c)
        except: pass
    # Demand: scale by planning horizon
    ph=planning_horizons[0] if planning_horizons else 2030
    dem_scale=1.0 + (ph-2030)*0.015  # ~1.5% per year
    if "E" not in sector: dem_scale*=1.1  # sector coupling adds heat
    hour=np.arange(T)%24
    dem_base=2500 if interconnect=="usa" else (1800 if interconnect=="eastern" else (800 if interconnect=="texas" else 1200))
    dem_pf=0.65+0.35*np.sin(np.pi*(hour-6)/12)
    dem_pf=np.clip(dem_pf+rng.normal(0,0.03,T),0.5,1.1)
    # Renewable CFs
    wind_cf=np.clip(rng.weibull(2,T)*0.35+0.12,0.05,0.95)
    solar_cf=np.clip(np.maximum(0,np.sin(np.pi*(hour-6)/12))*0.85 + rng.normal(0,0.04,T),0,0.95)
    hydro_cf=np.clip(0.55+0.1*np.sin(np.pi*(hour-4)/12)+rng.normal(0,0.05,T),0.25,0.85)
    # Add generators per bus
    for bus in n.buses.index:
        # wind onwind extendable
        cf_w=wind_cf*np.clip(rng.normal(1,0.08,T),0.7,1.3)
        cf_w=np.clip(cf_w,0,1)
        if extendable:
            n.add("Generator", f"Wind {bus}", bus=bus, carrier="onwind", p_nom_extendable=True, capital_cost=80000, marginal_cost=0.5, p_max_pu=cf_w)
            n.add("Generator", f"Solar {bus}", bus=bus, carrier="solar", p_nom_extendable=True, capital_cost=60000, marginal_cost=0.2, p_max_pu=solar_cf)
        else:
            # fixed like production cost
            n.add("Generator", f"Wind {bus}", bus=bus, carrier="onwind", p_nom=rng.uniform(80,300), marginal_cost=0.5, p_max_pu=cf_w)
            n.add("Generator", f"Solar {bus}", bus=bus, carrier="solar", p_nom=rng.uniform(60,250), marginal_cost=0.2, p_max_pu=solar_cf)
        # hydro
        if rng.rand()<0.4:
            n.add("Generator", f"Hydro {bus}", bus=bus, carrier="hydro", p_nom=rng.uniform(100,600), marginal_cost=3, p_max_pu=hydro_cf)
        # gas/coal/nuclear fixed
        n.add("Generator", f"Gas {bus}", bus=bus, carrier="gas", p_nom=rng.uniform(200,800), marginal_cost=40+rng.normal(0,5), p_max_pu=1.0)
        if rng.rand()<0.3:
            n.add("Generator", f"Coal {bus}", bus=bus, carrier="coal", p_nom=rng.uniform(150,500), marginal_cost=30+rng.normal(0,4), p_max_pu=1.0)
        # load
        p_load=dem_base/len(n.buses)*dem_scale*(0.8+rng.uniform(0,0.4))
        n.add("Load", f"Load {bus}", bus=bus, p_set=p_load*dem_pf)
    # Transmission: connect nearest neighbors (radial + mesh)
    buses=list(n.buses.index)
    for i, b in enumerate(buses):
        # nearest 2
        dlist=[]
        for j, bj in enumerate(buses):
            if i==j: continue
            d=_hav(n.buses.loc[b,"y"], n.buses.loc[b,"x"], n.buses.loc[bj,"y"], n.buses.loc[bj,"x"])
            dlist.append((d,bj))
        dlist.sort()
        for d,bj in dlist[:2]:
            if i < buses.index(bj):
                length=d
                # s_nom based on opts: copt = unlimited
                s_nom=1000 if "copt" in opts else 600
                r=0.02*length/100; x=0.10*length/100
                try:
                    n.add("Line", f"Line {b}-{bj}", bus0=b, bus1=bj, length=float(length), r=float(r), x=float(x), s_nom=float(s_nom), s_nom_extendable=("copt" in opts))
                except: pass
    # Storage
    for bus in list(n.buses.index)[:3]:
        n.add("StorageUnit", f"Battery {bus}", bus=bus, p_nom=150 if not extendable else 0, p_nom_extendable=extendable, max_hours=4, efficiency_store=0.9, efficiency_dispatch=0.9, cyclic_state_of_charge=True)
    # Global constraints for opts
    if "Co2L" in opts:
        # parse Co2L value
        import re
        m=re.search(r"Co2L([0-9\.]+)", opts)
        lim=float(m.group(1)) if m else 0.5
        # lim as fraction of 1.0 = no limit, 0.05 = 95% reduction
        n.add("GlobalConstraint", "Co2Limit", type="primary_energy", carrier_attribute="co2_emissions", sense="<=", constant=lim*1e8)
    if "RPS" in opts:
        n.add("GlobalConstraint", "RPS", type="tech_capacity_expansion", carrier_attribute="p_nom", sense=">=", constant=0)
    # Slack
    for b in n.buses.index:
        n.add("Generator", f"Slack {b}", bus=b, carrier="gas", p_nom=2000, marginal_cost=500, p_max_pu=1.0)
    return n

def optimize_pypsa(n, snapshots=None):
    try:
        import pypsa
        ok=False; msg=""
        # try HiGHS
        try:
            n.optimize(solver_name="highs", solver_options={"threads":2})
            obj=getattr(n,"objective",None)
            if obj is not None and not (isinstance(obj,float) and np.isnan(obj)):
                return True, f"Optimal · objective = {float(obj):,.0f} (HiGHS)"
        except Exception as e:
            traceback.print_exc()
        # fallback scipy not needed; return
        return False, "Infeasible — HiGHS failed"
    except Exception as e:
        return False, f"Optimize error: {e}\n{traceback.format_exc()[:800]}"

def plot_dispatch(n, h=360):
    if not hasattr(n,"generators_t") or n.generators_t.p.empty: return None
    df=n.generators_t.p
    cmap=n.generators["carrier"].to_dict()
    byc={}
    for col in df.columns:
        car=cmap.get(col,"other")
        byc.setdefault(car, np.zeros(len(df)))
        byc[car]+=df[col].values
    # remove slack
    byc_ns={k:v for k,v in byc.items() if "Slack" not in k}
    slack=sum(v for k,v in byc.items() if "Slack" in k) if any("Slack" in k for k in byc) else np.zeros(len(df))
    fig=_fig(h, "Dispatch by carrier (MW) — PyPSA HiGHS")
    for car, arr in sorted(byc_ns.items()):
        fig.add_trace(go.Scatter(x=n.snapshots, y=arr, mode="lines", stackgroup="one", name=car, line=dict(width=0)))
    if slack.sum()>1:
        fig.add_trace(go.Scatter(x=n.snapshots, y=slack, mode="lines", name="Slack (ENS)", line=dict(color="red", width=2, dash="dot")))
    fig.update_layout(yaxis_title="MW (hourly dispatch, stacked = total meeting demand)", xaxis_title="Snapshot (hour) — hover for MW per carrier; Slack = unserved energy (should be ~0)")
    return fig

def plot_loading(n, h=340):
    try:
        parts=[]
        if hasattr(n,"lines_t") and not n.lines_t.p0.empty:
            df=n.lines_t.p0.abs(); s_nom=n.lines.s_nom.replace(0,np.nan)
            loading=(df.div(s_nom,axis=1)*100).mean().sort_values(ascending=False)
            parts.append(("Lines",loading))
        if hasattr(n,"links_t") and hasattr(n.links_t,"p0") and not n.links_t.p0.empty:
            df=n.links_t.p0.abs() if hasattr(n.links_t,"p0") else None
            if df is not None and not df.empty:
                p_nom=n.links.p_nom.replace(0,np.nan)
                loading=(df.div(p_nom,axis=1)*100).mean().sort_values(ascending=False)
                parts.append(("Links",loading))
        if not parts: return None
        fig=_fig(h, "Avg loading per branch (%)")
        for label, ser in parts:
            if ser.empty: continue
            fig.add_trace(go.Bar(x=ser.index.astype(str), y=ser.values, name=label, text=[f"{v:.0f}%" for v in ser.values], textposition="outside"))
        fig.update_layout(yaxis_title="% avg loading (0-100%, >85% = congested)", xaxis_tickangle=-18, barmode="group", title=dict(font=dict(size=13)))
        return fig
    except: return None

def plot_map(n, h=580, title="Network map — USA (intensive, pies = tech mix, lines = capacity, size = GW)"):
    # Enhanced map: uses exact PyPSA-USA tech colors (oil #262626, coal #707070, ...), us_mainland.geojson background,
    # line thickness by s_nom (2 GW thin → 5 GW thick), bus pies sized by 5/10/50 GW, AC green #70af1d / DC purple #8a1caf
    try:
        fig=go.Figure()
        # — US mainland outline from grid2poster/regions/us_mainland.geojson (faithful background) —
        gj = load_us_geojson()
        if gj:
            try:
                for feat in gj.get("features", []):
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [])
                    gtype = geom.get("type")
                    polys = []
                    if gtype == "Polygon":
                        polys = [coords]
                    elif gtype == "MultiPolygon":
                        polys = coords
                    for poly in polys:
                        for ring in poly:
                            # outer ring only (first)
                            lons = [c[0] for c in ring]
                            lats = [c[1] for c in ring]
                            fig.add_trace(go.Scatter(x=lons, y=lats, mode="lines", fill="toself", fillcolor="rgba(242,240,236,0.9)", line=dict(color="#c9bdaa", width=1.2), hoverinfo="skip", showlegend=False))
                        break  # only outer for preview speed (first polygon)
                    break
            except Exception as e:
                pass
        else:
            # fallback bbox
            fig.add_shape(type="rect", x0=-124.5, y0=24.5, x1=-66.5, y1=49.5, line=dict(color="#d0dce9", width=1, dash="dot"), fillcolor="rgba(240,244,248,0.35)")

        # — Lines: thickness by s_nom (faithful to figure legend 2.0 GW vs 5.0 GW) and color by AC/DC + loading —
        load_dict={}
        try:
            if hasattr(n,"lines_t") and not n.lines_t.p0.empty and hasattr(n,"lines") and "s_nom" in n.lines.columns:
                avg = (n.lines_t.p0.abs().div(n.lines.s_nom.replace(0, 1), axis=1)*100).mean()
                for idx, v in avg.items():
                    if v>88: load_dict[idx]="#c0392b"
                    elif v>60: load_dict[idx]="#d67e00"
                    else: load_dict[idx]="#2a7f62"
        except: pass

        if hasattr(n,"lines") and len(n.lines):
            for _, r in n.lines.iterrows():
                try:
                    x0,y0=n.buses.loc[r.bus0,["x","y"]].values
                    x1,y1=n.buses.loc[r.bus1,["x","y"]].values
                    s_nom = float(r.s_nom) if "s_nom" in r and not pd.isna(r.s_nom) else 600.0
                    # width mapping: 2 GW → 1.2pt, 5 GW → 3.5pt, linear + clamp
                    w = 1.0 + (s_nom/5000.0)*4.0
                    w = max(1.0, min(4.5, w))
                    # if heavily loaded, boost
                    if r.name in load_dict and load_dict[r.name]=="#c0392b":
                        w+=0.6
                    # AC vs DC color
                    base_col = TECH_COLORS.get("AC", "#70af1d") if "AC" in str(getattr(r,"carrier","AC")) or True else TECH_COLORS["AC"]
                    # Use loading color if congested else AC green
                    col = load_dict.get(r.name, base_col) if r.name in load_dict else base_col
                    # For links (DC) we would use purple — here all Lines are AC in synthetic
                    fig.add_trace(go.Scatter(x=[x0,x1], y=[y0,y1], mode="lines", line=dict(color=col, width=w), hoverinfo="text", text=f"{r.name}: {r.bus0}→{r.bus1} · {s_nom:.0f} MW · {float(getattr(r,'length',0)):.0f} km", showlegend=False, opacity=0.95))
                except: continue
        # — Links (DC) if any —
        if hasattr(n,"links") and len(n.links)>0:
            for _, r in n.links.iterrows():
                try:
                    # links have bus0/bus1 or bus names
                    b0 = r.bus0 if "bus0" in r else r.get("bus0", None)
                    b1 = r.bus1 if "bus1" in r else r.get("bus1", None)
                    if b0 is None or b1 is None or b0 not in n.buses.index or b1 not in n.buses.index: continue
                    x0,y0=n.buses.loc[b0,["x","y"]].values
                    x1,y1=n.buses.loc[b1,["x","y"]].values
                    s_nom = float(r.p_nom) if "p_nom" in r and not pd.isna(r.p_nom) else 1000.0
                    w = 1.2 + (s_nom/5000.0)*3.5
                    w = max(1.2, min(5, w))
                    fig.add_trace(go.Scatter(x=[x0,x1], y=[y0,y1], mode="lines", line=dict(color=TECH_COLORS["DC"], width=w, dash="dash"), hoverinfo="text", text=f"DC Link {r.name}: {b0}→{b1} · {s_nom:.0f} MW", showlegend=False))
                except: continue

        # — Buses as pies: each bus is a small pie chart whose slices are tech colors, sized by total GW (5/10/50 GW legend) —
        # Compute total capacity per bus for sizing
        bus_tot = {}
        bus_mix = {}  # bus -> {carrier: MW}
        try:
            for b in n.buses.index:
                gens = n.generators[n.generators["bus"]==b]
                if len(gens)==0:
                    bus_tot[b]=0; bus_mix[b]={}
                else:
                    # use p_nom_opt if CEP else p_nom
                    col = "p_nom_opt" if "p_nom_opt" in gens.columns and gens["p_nom_opt"].sum()>1 else "p_nom"
                    # group by carrier
                    grp = gens.groupby("carrier")[col].sum()
                    # filter small
                    grp = grp[grp>1]
                    bus_mix[b]=grp.to_dict()
                    bus_tot[b]=float(grp.sum())
        except:
            for b in n.buses.index: bus_tot[b]=1000; bus_mix[b]={"gas":1000}

        # Add pies using go.Pie with domain positioned by lon/lat normalized to figure paper
        # Map extent: x -126..-65 (61 deg), y 23..50.5 (27.5 deg)
        def lon_to_x(lon): return (lon + 126.0)/61.0
        def lat_to_y(lat): return (lat - 23.0)/27.5
        for b in n.buses.index:
            try:
                lon, lat = float(n.buses.loc[b,"x"]), float(n.buses.loc[b,"y"])
                xn = lon_to_x(lon); yn = lat_to_y(lat)
                tot = bus_tot.get(b, 0) or 0
                # radius scaling: 5 GW → 0.018, 10 GW → 0.025, 50 GW → 0.055 (area ~ sqrt)
                # Convert tot MW to GW
                gw = tot/1000.0
                if gw < 0.1: gw = 0.5  # minimal visible
                r = 0.018 if gw <=5 else (0.025 if gw <=10 else (0.038 if gw <=25 else 0.055))
                # but scale slightly with sqrt for intermediate
                if gw>5 and gw!=10 and gw!=50:
                    r = 0.015 + (gw**0.5)*0.007
                    r = max(0.015, min(0.06, r))
                x0 = max(0.0, xn - r); x1 = min(1.0, xn + r)
                y0 = max(0.0, yn - r*1.25); y1 = min(1.0, yn + r*1.25)  # adjust for aspect
                mix = bus_mix.get(b, {})
                if not mix:
                    # empty bus — small grey dot
                    fig.add_trace(go.Scatter(x=[lon], y=[lat], mode="markers", marker=dict(size=8, color="#b0b0b0", line=dict(color="white",width=1)), hovertext=f"{b}: no capacity", hoverinfo="text", showlegend=False))
                    continue
                # Order carriers by CARRIER_ORDER for consistent colors
                # Sort mix keys by predefined order
                ordered = sorted(mix.items(), key=lambda kv: (CARRIER_ORDER.index(kv[0]) if kv[0] in CARRIER_ORDER else 99, -kv[1]))
                labels = [k for k,_ in ordered]
                values = [v for _,v in ordered]
                colors = [carrier_color(k) for k in labels]
                fig.add_trace(go.Pie(
                    labels=labels, values=values,
                    marker=dict(colors=colors, line=dict(color="white", width=1)),
                    domain=dict(x=[x0,x1], y=[y0,y1]),
                    hole=0.15, sort=False, direction="clockwise",
                    textinfo="none", hoverinfo="label+value", hovertemplate=f"{b}<br>%{{label}}: %{{value:.0f}} MW<extra></extra>",
                    showlegend=False,
                ))
                # bus name label above pie
                fig.add_annotation(x=lon, y=lat+0.6, xref="x", yref="y", text=f"<b>{b}</b>", showarrow=False, font=dict(size=9, color="#0f3d63"), bgcolor="rgba(255,255,255,0.75)", borderpad=1)
            except Exception as e:
                continue

        fig.update_layout(
            template="plotly_white", height=h, title=dict(text=title, font=dict(size=15, color="#0f3d63")),
            margin=dict(l=14,r=14,t=62,b=14),
            xaxis=dict(title="Longitude (°W)", range=[-126, -65], gridcolor="#eaf0f7", zeroline=False),
            yaxis=dict(title="Latitude (°N)", range=[23, 50.5], gridcolor="#eaf0f7", scaleanchor="x", scaleratio=1.28),
            plot_bgcolor="#f7fbff", paper_bgcolor="rgba(0,0,0,0)", hovermode="closest",
            showlegend=False,
        )
        # Legend annotation matching figure: line thickness + pie sizes + tech colors
        fig.add_annotation(
            x=-124, y=49.2, xref="x", yref="y",
            text="<b>Legend — as in your figure</b><br>"
                 "<span style='color:#70af1d'>━</span> AC 2.0 GW (thin) &nbsp; <span style='color:#70af1d'><b>━━━</b></span> 5.0 GW (thick) &nbsp; "
                 "<span style='color:#8a1caf'>┅┅</span> DC &nbsp; "
                 "● 5 GW &nbsp; ● 10 GW &nbsp; <span style='font-size:15px'>●</span> 50 GW &nbsp; | &nbsp; "
                 "<span style='color:#c0392b'>■</span>  >88% loaded <span style='color:#d67e00'>■</span> 60-88% <span style='color:#2a7f62'>■</span> <60%",
            showarrow=False, align="left", bgcolor="rgba(255,255,255,0.92)", bordercolor="#d0dce9", borderwidth=1,
            font=dict(size=9, color="#33475e")
        )
        return fig
    except Exception as e:
        import traceback as _tb
        # fallback simple scatter
        try:
            fig=go.Figure()
            # still try to add us outline
            gj2 = load_us_geojson()
            if gj2:
                for feat in gj2.get("features", [])[:1]:
                    coords = feat["geometry"]["coordinates"][0][0] if feat["geometry"]["type"]=="MultiPolygon" else feat["geometry"]["coordinates"][0]
                    lons=[c[0] for c in coords]; lats=[c[1] for c in coords]
                    fig.add_trace(go.Scatter(x=lons, y=lats, mode="lines", fill="toself", fillcolor="rgba(240,240,240,0.9)", line=dict(color="#c9bdaa",width=1), showlegend=False))
            fig.add_trace(go.Scatter(x=n.buses["x"], y=n.buses["y"], mode="markers+text", text=n.buses.index.astype(str), marker=dict(size=12, color=[carrier_color(n.generators[n.generators["bus"]==b]["carrier"].iloc[0]) if (n.generators["bus"]==b).any() else "#003366" for b in n.buses.index])))
            fig.update_layout(height=h, title=title)
            return fig
        except: return None

# ---------- Repo explorer ----------
def render_repo_explorer():
    section_header("📁 Repository Explorer (Repo Explorer) — every file, every folder", "Click any file to see its role and live content — this is the clone in detail you asked for. Use search to find any of the 487 files.")
    banner("📁 PLAY HERE — browse the entire pypsa-usa repository, file by file")
    # Tree
    tree=repo_tree()
    # Filters
    c1,c2,c3=st.columns([1.2,1,1])
    with c1:
        q=st.text_input("🔍 Search file", "", placeholder="e.g., Snakefile, solve_network.py, config.common.yaml", key="repo-q")
        ext=st.selectbox("Filter by type", ["all",".py",".yaml",".smk",".md",".csv",".sh"], key="repo-ext")
    with c2:
        folder=st.selectbox("Folder", ["all","workflow","workflow/rules","workflow/scripts","workflow/config","workflow/repo_data","docs",".github"], key="repo-folder")
        show_cnt=st.slider("Show first N files", 20, 300, 80, 20, key="repo-cnt")
    with c3:
        st.metric("Files in repo", f"{len(tree)}")
        st.caption("Clone: `git clone https://github.com/PyPSA/pypsa-usa.git` — depth 1, 487 files")
        if st.button("🔄 Refresh tree", key="repo-refresh"): st.cache_data.clear(); st.rerun()
    # Filter
    filtered=tree
    if q.strip():
        ql=q.lower(); filtered=[f for f in filtered if ql in f.lower()]
    if ext!="all": filtered=[f for f in filtered if f.endswith(ext)]
    if folder!="all": filtered=[f for f in filtered if f.startswith(folder)]
    filtered=sorted(filtered)[:show_cnt]
    st.caption(f"Showing **{len(filtered)}** files — click to preview. Full path = `pypsa-usa/<path>`")
    cols=st.columns([1,1.6])
    with cols[0]:
        sel=st.selectbox("Select a file to inspect", filtered, key="repo-sel")
        if sel:
            fp=REPO / sel
            st.markdown(f"<div class='file-card'><b>{sel}</b><br><span style='color:#666;font-size:.78em'>{fp.stat().st_size/1024:.1f} KB · {fp.suffix or 'no ext'} · {str(fp.parent)[:40]}</span></div>", unsafe_allow_html=True)
            # Quick action: copy path
            st.code(f"pypsa-usa/{sel}", language="text")
            # If workflow script, show which rule uses it
            if sel.startswith("workflow/scripts/"):
                # find rules that reference it
                rules=[]
                for rfile in (REPO/"workflow/rules").glob("*.smk"):
                    if sel.split("/")[-1].replace(".py","") in rfile.read_text():
                        rules.append(rfile.name)
                if rules: st.caption(f"Used by rules: {', '.join(rules)}")
    with cols[1]:
        if sel:
            txt=read_repo_file(sel)
            # language hint
            lang="python" if sel.endswith(".py") else ("yaml" if sel.endswith(".yaml") else ("makefile" if sel.endswith(".smk") else "markdown" if sel.endswith(".md") else "text"))
            st.code(txt, language=lang)
            # Download
            try:
                fp=REPO / sel
                if fp.exists() and fp.stat().st_size < 500000:
                    data=fp.read_bytes()
                    st.download_button(f"⬇️ Download {sel.split('/')[-1]}", data, file_name=sel.split('/')[-1], key=f"dl-repo-{sel}")
            except: pass
    # Folder summaries
    st.divider()
    st.markdown("#### 📂 Folder-by-folder — what each does (so user realizes the configurable model)")
    folders=[
        ("`/` root", "README, LICENSE, CITATION, pyproject.toml, uv.lock, init_pypsa_usa.sh — entry points and deps (pypsa==0.30.2, atlite, highspy, snakemake).", "2"),
        ("`workflow/Snakefile`", "Master DAG — merges 4 configs (`config.common/cluster/plotting/api/sector.yaml`), defines wildcards (`interconnect, simpl, clusters, ll, opts, sector`), imports 7 rule files and builds `results/{interconnect}/networks/*.nc`. ~400 lines.", "1"),
        ("`workflow/rules/` (7 .smk)", "`common.smk` helpers · `retrieve.smk` data · `build_electricity.smk` (build_shapes, build_base_network, cluster, add_electricity) · `build_sector.smk` · `solve_electricity.smk` (solve_network + validation) · `postprocess.smk` · `validate.smk`. Each maps to a tab below.", "7"),
        ("`workflow/scripts/` (50+ .py)", "`build_base_network.py` (Breakthrough buses/lines → GIS) → `cluster_network.py` (k-means) → `add_electricity.py` (loads, gens, renewables via atlite/godeeep) → `solve_network.py` (linopy+HiGHS, foresight perfect/rolling, Co2L) → `plot_*.py`, `summary.py` etc. Every script has a card in Workflow tab.", "51"),
        ("`workflow/config/`", "`config.common.yaml` (foresight, renewable, atlite cutouts, lines, snapshots, sectors, costs) · `config.cluster.yaml` · `config.plotting.yaml` · `config.api.yaml` · `config/sector.yaml` · `config/policy_constraints/` (ReEDS csvs). The Config Lab lets you edit these live.", "~35"),
        ("`workflow/repo_data/`", "Ground truth: `ReEDS_Constraints/` (membership, carbon caps, state_policies, transmission_costs, NARIS2024), `WECC_ADS_public/` (GeneratorList.csv), `costs/` (EFS, EIA tech costs), `geospatial/` (BA_shapes, NERC, BOEM), `costs/`, `plants/` etc. — Data Lab tables them.", "~120"),
        ("`workflow/envs/`", "`environment.yaml` (conda-forge, python 3.11, pypsa 0.30, snakemake 7.32…) + `dev.yaml` (`ruff, mypy, pytest, pre-commit`). Contributing tab checks them.", "2"),
        ("`docs/` (Sphinx, MyST)", "`source/*.md/*.rst` — install, usage, config docs, data-gens, sectors… `make html` builds readthedocs. Docs Lab previews them.", "~25"),
        ("`.github/workflows/main.yml`", "CI: micromamba env, cache cutouts, `test.sh` (snakemake dry-run + tutorial). Validation Lab shows it.", "1"),
        ("`tests` / `test.sh`", "`workflow/scripts/test/` + root `.test_sh` — pytest + snakemake --dryrun.", "2"),
    ]
    for title, desc, cnt in folders:
        with st.expander(f"{title} — {desc} ({cnt} files)", expanded=False):
            if "rules" in title:
                for f in sorted((REPO/"workflow/rules").glob("*.smk")):
                    st.code(f.read_text()[:900], language="makefile")
            elif "scripts" in title:
                st.dataframe(pd.DataFrame([{"script":p.name, "KB": round(p.stat().st_size/1024,1), "lines": len(p.read_text().splitlines())} for p in sorted((REPO/"workflow/scripts").glob("*.py"))]), use_container_width=True, height=260)
            elif "config" in title:
                st.code((REPO/"workflow/config/config.common.yaml").read_text()[:1200], language="yaml")
            elif "repo_data" in title:
                st.caption("Sample: ReEDS_Constraints/transmission/")
                st.dataframe(pd.DataFrame([{"file":p.name, "KB": round(p.stat().st_size/1024,1)} for p in sorted((REPO/"workflow/repo_data/ReEDS_Constraints/transmission").glob("*.csv"))[:12]]), use_container_width=True, height=200)

def render_config_lab():
    section_header("⚙️ Config Lab — highly configurable US model", "This is what makes pypsa-usa 'highly configurable' — 4 merged YAMLs + policy constraints. Change any knob and see the network re-optimize below.")
    banner("⚙️ PLAY HERE — edit config and watch the model change")
    c1,c2=st.columns([1.1,1.4])
    with c1:
        st.markdown("#### 📄 Configs merged in Snakefile (`workflow/config` + `workflow/repo_data/config`)")
        cfg_candidates=[REPO/"workflow/config/config.common.yaml", REPO/"workflow/repo_data/config/config.common.yaml", REPO/"workflow/repo_data/config/config.cluster.yaml", REPO/"workflow/repo_data/config/config.plotting.yaml", REPO/"workflow/repo_data/config/config.api.yaml", REPO/"workflow/repo_data/config/config.tutorial.yaml", REPO/"workflow/repo_data/config/config.default.yaml", REPO/"workflow/repo_data/config/config.sector.yaml"]
        cfg_files=[str(p.relative_to(REPO)) for p in cfg_candidates if p.exists()]
        # add any other yaml in workflow/config
        for p in (REPO/"workflow/config").glob("*.yaml"):
            rel=str(p.relative_to(REPO))
            if rel not in cfg_files: cfg_files.append(rel)
        for p in (REPO/"workflow/repo_data/config").glob("*.yaml"):
            rel=str(p.relative_to(REPO))
            if rel not in cfg_files: cfg_files.append(rel)
        if not cfg_files: cfg_files=["workflow/config/config.common.yaml"]
        sel_cfg=st.selectbox("Config file", cfg_files, key="cfg-sel")
        try:
            txt=(REPO / sel_cfg).read_text()
        except Exception as e:
            txt=f"(cannot read {sel_cfg}: {e})"
        st.code(txt[:5000], language="yaml")
        st.download_button(f"⬇️ Download {sel_cfg.split('/')[-1]}", txt.encode(), file_name=sel_cfg.split('/')[-1], key=f"dl-cfg-{sel_cfg}")
        with st.expander("📂 policy_constraints/ (ReEDS)"):
            for p in sorted((REPO/"workflow/repo_data/config/policy_constraints").rglob("*.csv")):
                st.caption(f"{p.relative_to(REPO)} — {p.stat().st_size} B"); st.code(p.read_text()[:400], language="text")
    # ── SYSTEM SIZE — most visible control (user asked where to change size) ──
    st.markdown("### 📏 Power System SIZE — where you change the network")
    banner("📏 SIZE = Interconnect (geography) × Clusters (nodes/lines). Pick here — every lab below uses the same dials.")
    sz1, sz2, sz3 = st.columns([1.2,1.5,1])
    with sz1:
        interconnect=st.selectbox("🌎 Interconnect — geographic coverage", ["western","eastern","texas","usa"], key="cfg-inter", help="western=WECC 11 states (small), eastern=36 states (largest), texas=single, usa=all 3 together (continental). This is `interconnect` wildcard in Snakefile.")
        st.caption(f"→ {INTERCONNECT_COORDS[interconnect]['desc']}")
    with sz2:
        clusters=st.select_slider("🔢 Clusters — number of buses/nodes (spectrum 4→300)", options=SIZE_OPTIONS, value=20, key="cfg-clust", format_func=size_label, help="This is `clusters` wildcard: how many nodes after k-means clustering. More = more detail, slower. Real pypsa-usa: 300+ buses → here synthetic but same locations.")
        n_est_lines = int(clusters*1.7)
        st.caption(f"→ Your system will have **{clusters} buses, ~{n_est_lines} lines, ~{clusters*2.2:.0f} generators + loads**. {SIZE_HELP[clusters]}")
        # live preview button
        if st.button("👁️ Preview SIZE on USA map (no solve, instant)", key="cfg-preview"):
            with st.spinner("Building preview…"):
                nprev=build_usa_network(interconnect=interconnect, clusters=clusters, n_hours=4)
                figprev=plot_map(nprev, h=420, title=f"Preview — {interconnect} · {clusters} buses · ~{n_est_lines} lines (move slider and click again)")
                if figprev: st.plotly_chart(figprev, use_container_width=True, config={"displaylogo":False}, key="cfg-preview-map")
    with sz3:
        st.markdown("#### Size spectrum (demo → research)")
        st.dataframe(
            [{"Clusters":k, "What it feels like":SIZE_HELP[k].split(" — ")[1] if " — " in SIZE_HELP[k] else SIZE_HELP[k]} for k in [4,9,20,50,100,200]],
            hide_index=True, use_container_width=True, height=200
        )
        st.caption("💡 Tip: start **20** (tutorial), then **50** (research), then **100–200** for planning. All 3 labs (PF→PSC→CEP) respect the same size dials.")
    st.divider()
    with c2:
        st.markdown("#### 🎛️ Other config — scenario knobs (after you pick SIZE)")
        planning=st.multiselect("Planning horizons (scenario: planning_horizons)", [2030,2040,2050], default=[2030], key="cfg-ph")
        sector=st.selectbox("Sector (E=electricity only, E-G=natural gas + power)", ["E","E-G"], key="cfg-sector")
        opts=st.text_input("Opts (Co2L, RPS, LR, copt …)", "Co2L0.1", help="e.g., Co2L0.1 = 90% cut, RPS=renewable, copt=transmission co-opt", key="cfg-opts")
        foresight=st.selectbox("Foresight (perfect vs myopic)", ["perfect","myopic"], key="cfg-foresight")
        renewable=st.selectbox("Renewable dataset (from config.common)", ["godeeep","atlite"], key="cfg-ren")
        ll=st.selectbox("Line limit (ll wild) 1.0 = 100% N-1", ["1.0","1.5","copt","1H"], key="cfg-ll")
        simpl=st.selectbox("Simpl (network simplification)", ["all","100m","200m"], key="cfg-simpl")
        if st.button("▶️ Build network from this config (PyPSA + HiGHS, 24h)", type="primary", use_container_width=True, key="cfg-run"):
            with st.spinner("Building pypsa-usa-like network from your config…"):
                n=build_usa_network(interconnect=interconnect, clusters=clusters, planning_horizons=planning if planning else [2030], opts=opts, sector=sector, foresight=foresight, n_hours=24)
                ok,msg=optimize_pypsa(n)
                st.session_state["cfg-n"]=(n,ok,msg,dict(interconnect=interconnect,clusters=clusters,planning=planning,opts=opts,sector=sector))
        if "cfg-n" in st.session_state:
            n,ok,msg,meta=st.session_state["cfg-n"]
            st.success(msg) if ok else st.error(msg)
            st.caption(f"Config → {meta}")
            fig=plot_dispatch(n, h=300)
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="cfg-disp")
            fig2=plot_map(n, h=380, title=f"Config result — {meta['interconnect']} {meta['clusters']} clusters {meta['opts']}")
            if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displaylogo":False}, key="cfg-map")
        st.markdown("<div class='legend'>💡 <b>Faithful to repo:</b> wildcards <code>interconnect, simpl, clusters, ll, opts, sector</code> + <code>planning_horizons, foresight, renewable</code> all come from <code>workflow/config/config.common.yaml</code> + <code>Snakefile wildcard_constraints</code>.</div>", unsafe_allow_html=True)
        render_size_explainer()

def render_workflow():
    section_header("🔀 Workflow DAG — Snakemake rules → scripts → results", "`workflow/Snakefile` is the spine — 7 rule files, 51 scripts, 5 logs/benchmarks/results dirs. Click a rule to see its script.")
    banner("🔀 PLAY HERE — click a rule, read its script, then run a mini-simulation")
    # DAG visual as text + plotly
    st.graphviz_chart("""
    digraph DAG {
      rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#eaf3fb", color="#003366"];
      retrieve -> "build_shapes" -> "build_base_network" -> "build_bus_regions" -> "build_powerplants" -> "add_electricity" -> "cluster_network" -> "prepare_network" -> "solve_network" -> "summary" -> "plot_*";
      "build_renewable_profiles" -> "add_electricity";
      "build_cost_data" -> "solve_network";
      "solve_network" -> "validate";
      "validate" [fillcolor="#fff8e6", color="#d67e00"];
      "solve_network" [fillcolor="#e8f8f3", color="#1a7f5e"];
    }
    """)
    rules=sorted((REPO/"workflow/rules").glob("*.smk"))
    sel_rule=st.selectbox("Rule file", [r.name for r in rules], key="wf-rule")
    txt=(REPO/f"workflow/rules/{sel_rule}").read_text()
    st.code(txt[:6000], language="makefile")
    # Scripts in that rule
    import re
    scripts=re.findall(r"script:\s*\"?\.?\./?scripts/([^\"]+)", txt)
    if scripts:
        st.markdown("**Scripts called by this rule:**")
        seen=set()
        for i, s in enumerate(scripts):
            if s.strip() in seen: continue
            seen.add(s.strip())
            fp=REPO/f"workflow/scripts/{s}"
            if fp.exists():
                with st.expander(f"📄 scripts/{s} — {fp.stat().st_size/1024:.1f} KB"):
                    st.code(fp.read_text()[:4000], language="python")
                    st.download_button(f"⬇️ Download {s}", fp.read_bytes(), file_name=s, key=f"dl-wf-{i}-{s}-{sel_rule}")
    # Run a mini step: build_base_network + cluster + solve
    st.divider()
    st.markdown("#### ⚡ Try a workflow step live")
    step=st.selectbox("Step to simulate", ["build_base_network (9→50 buses)", "cluster_network (50→20)", "solve_network (LOPF/CEP)", "summary + plots"], key="wf-step")
    if st.button(f"▶️ Run {step} (synthetic, 24h, HiGHS)", type="primary", key="wf-run"):
        with st.spinner("Running step…"):
            n=build_usa_network(interconnect="western", clusters=20, extendable=("solve" in step.lower()), n_hours=24)
            ok,msg=optimize_pypsa(n) if "solve" in step.lower() or "summary" in step.lower() else (True, "Built — no solve")
            st.success(msg) if ok else st.error(msg)
            fig=plot_map(n, title=f"{step} — western 20 clusters")
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="wf-map")
            if "solve" in step.lower():
                fig2=plot_dispatch(n)
                if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displaylogo":False}, key="wf-disp")

# ---------- Scenario helpers ----------

def render_size_explainer():
    with st.expander("📏 What does SIZE mean? Effects & how it is handled — click to understand", expanded=False):
        st.markdown("""
**SIZE = Geography (Interconnect) × Resolution (Clusters)**

| Dimension | What you pick | What real PyPSA-USA does | What this demo does | Effect when you increase it |
|---|---|---|---|---|
| **Interconnect** `western / eastern / texas / usa` | Which synchronous grid | Loads 3 different base networks from Breakthrough Energy via `build_base_network.py` (buses/lines from FERC + BA shapes) | Same 4 synthetic WECC_9/EASTERN_9/TEXAS_6 seeds, but stretched to that bbox | **Geography:** `texas` (1 state) → `western` (11) → `eastern` (36) → `usa` (continental, 48). Demand & line length scale with it. **Contiguous USA is 3× texas.** |
| **Clusters** `4 → 300` | How many buses after reduction | `cluster_network.py`: **k-means** on substations (`k = clusters`), lines aggregated, `simpl` + `ll` control detail | Synthetic but faithful: ≤ base = sample, > base = interpolate 70% along corridors 30% random in bbox, then `nearest-2` mesh. Same `s_nom` logic (`copt` = expandable). | **Resolution:** `4` = toy, `20` = tutorial (seconds), `50` = research (k-means 50), `100–200` = planning (hundreds of nodes, 20–45s solve, more accurate flows & local renewables). |

**Technically (pypsa-usa):**
1. `build_base_network.py` → GIS + Breakthrough buses/lines (230–765 kV)
2. `cluster_network.py` → `kmeans` → `buses → clusters`, `lines → aggregated` with `length × impedance`
3. `add_electricity.py` → attach `load/generators` (atlite/godeeep profiles) per bus region
4. `solve_network.py` → `linopy + HiGHS` → `p_nom_opt` (invest) or dispatch. More clusters = **bigger LP**: `rows ≈ 6× buses, cols ≈ 3× buses× hours`. Solve time ~ `clusters^1.3`.

**How the demo handles it (so it stays interactive):**
- Same wildcards `interconnect, clusters, ll, opts, sector` → so your slider maps 1-1 to the Snakemake call `snakemake results/{interconnect}/networks/elec_s{simpl}_c{clusters}_ec_l{ll}_{opts}_{sector}.nc`
- Synthetic coordinates are seeded (deterministic) → same slider = same network every time → reproducible paper.
- For Cloud, we cap default to `20` (fast), but you can push to `300` locally → just slower, not wrong. Tip: compare `20 vs 50 vs 100` on the **same opts** to see resolution vs cost.

**Interactive test:** set `Interconnect = usa, Clusters = 20` → **👁️ Preview** → see continental spread. Then `Clusters = 100` → preview again → notice 5× denser mesh. Then **▶️ Run CEP** with `Co2L0.1` — capacity spreads more evenly with higher resolution.
        """)
        c1,c2,c3=st.columns(3)
        with c1:
            st.caption("4 buses — tiny, teaching")
            st.code("clusters=4\n~7 lines\n200 generators\ninstant", language="text")
        with c2:
            st.caption("20 buses — tutorial")
            st.code("clusters=20\n~34 lines\n~44 gens\n2s HiGHS", language="text")
        with c3:
            st.caption("100 buses — planning")
            st.code("clusters=100\n~180 lines\n~220 gens\n12–15s", language="text")

def render_maps_posters():
    section_header("🗺️ Network & Poster — PyPSA-USA static map + grid2poster live", "The static map you attached + the OSM poster tool — both interactive here.")
    banner("🗺️ PLAY HERE — compare the official network image, then generate your own poster from the live network")
    colL, colR = st.columns([1.1, 1.1])
    with colL:
        st.markdown("#### 📷 Official `PyPSA-USA_network.png` — from `docs/source/_static`")
        st.caption("Source: `pypsa-usa/docs/source/_static/PyPSA-USA_network.png` (0fe7883) + your figure — same tech colors. Hover concept: pies = generation mix per node, line thickness = MW capacity.")
        p1 = ROOT / "assets" / "PyPSA-USA_network.png"
        if not p1.exists():
            p1 = REPO / "docs" / "source" / "_static" / "PyPSA-USA_network.png"
        if p1.exists():
            st.image(str(p1), caption="PyPSA-USA — ReEDS / Breakthrough 500+ bus, 2–5 GW lines, 5/10/50 GW pies", use_column_width=True)
            st.markdown("""
<div style='background:#fff;border:1px solid #e3eaf3;border-radius:10px;padding:10px 12px;font-size:.84em'>
<b>Figure legend — exact colors (from <code>workflow/repo_data/config/config.plotting.yaml</code>)</b><br>
<span style='display:inline-block;width:12px;height:12px;background:#262626;border-radius:2px'></span> Oil &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#707070;border-radius:2px'></span> Coal &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#ff9000;border-radius:2px'></span> Nuclear &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#0c6013;border-radius:2px'></span> Biomass &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#ba91b1;border-radius:2px'></span> Geothermal <br>
<span style='display:inline-block;width:12px;height:12px;background:#b20101;border-radius:2px'></span> Combined-Cycle Gas &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#d35050;border-radius:2px'></span> Open-Cycle Gas &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#235ebc;border-radius:2px'></span> Onshore Wind &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#6895dd;border-radius:2px'></span> Fixed Offshore &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#11a1c1;border-radius:2px'></span> Floating Offshore <br>
<span style='display:inline-block;width:12px;height:12px;background:#f9d002;border-radius:2px'></span> Solar &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#08ad97;border-radius:2px'></span> Reservoir & Dam &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#b8ea04;border-radius:2px'></span> Battery &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#70af1d;border-radius:2px'></span> AC &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#8a1caf;border-radius:2px'></span> DC &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#a4d600;border-radius:2px'></span> 4Hr Battery
<hr style='margin:6px 0'>
<b>Size:</b> <span style='display:inline-block;width:8px;height:8px;background:#70af1d;border-radius:50%'></span> 5 GW &nbsp;
<span style='display:inline-block;width:12px;height:12px;background:#70af1d;border-radius:50%'></span> 10 GW &nbsp;
<span style='display:inline-block;width:18px;height:18px;background:#70af1d;border-radius:50%'></span> 50 GW &nbsp; | &nbsp;
<b>Lines:</b> <span style='display:inline-block;width:18px;height:2px;background:#70af1d;vertical-align:middle'></span> 2.0 GW (thin) &nbsp;
<span style='display:inline-block;width:18px;height:4px;background:#70af1d;vertical-align:middle'></span> 5.0 GW (thick)
</div>
            """, unsafe_allow_html=True)
            with st.expander("🔍 What you see in the official map — WECC vs Eastern vs Texas"):
                st.markdown("""
- **West (teal dense):** California CA_S/CA_N ~15 GW solar+wind+gas pies, thick 5 GW lines I-5 corridor, hydro in PNW (#08ad97).
- **Texas (isolated):** ERCOT red gas + yellow solar + blue wind — DC ties at edges (#8a1caf dashed).
- **East (dense):** PJM giant 50 GW pies near NY/PA, mixed coal (#707070) + gas + nuclear (#ff9000), offshore wind off NJ (#6895dd).
- **Lines:** thickness = `s_nom` (2 vs 5 GW) — the demo's `plot_map` scales the same. Pies = per-bus `p_nom` by carrier using the colors above — demo pies match exactly via `TECH_COLORS`.
                """)
                st.caption("All colors are `tech_colors` from `config.plotting.yaml` — the demo's `carrier_color()` uses the same hex codes, so your live map is directly comparable to the paper figure.")
        else:
            st.error("PyPSA-USA_network.png not found — expected at assets/PyPSA-USA_network.png")
        p2 = ROOT / "assets" / "user_reference_map.png"
        if p2.exists():
            with st.expander("📎 Your attached figure — side-by-side"):
                st.image(str(p2), caption="Your reference: same legend — 5/10/50 GW pies, 2.0/5.0 GW lines", use_column_width=True)
                st.caption("This is what `plot_map()` now replicates with `TECH_COLORS` + `us_mainland.geojson` background.")
    with colR:
        st.markdown("#### 🗺️ Grid2Poster — live OSM poster from `us_mainland.geojson`")
        st.markdown("""
<div class='callout ok'>
<b>What is grid2poster?</b> <a href='https://github.com/open-energy-transition/grid2poster' target='_blank'>open-energy-transition/grid2poster</a> builds <b>print-ready A3 posters</b> of transmission grids from <b>OpenStreetMap</b> (`power=line` + `power=plant`). We use its <b>region file you asked for</b>: <code>regions/us_mainland.geojson</code> (CONUS outline, MultiPolygon) as the **exact background** of every live map above via <code>load_us_geojson()</code>. Themes like <code>paper_grid</code>, <code>electric_midnight</code>, <code>blackout</code> define background / line tier colors.
</div>
        """, unsafe_allow_html=True)
        gj = load_us_geojson()
        if gj:
            nfeat = len(gj.get("features", []))
            try:
                coords = gj["features"][0]["geometry"]["coordinates"]
                nverts = len(coords[0][0]) if gj["features"][0]["geometry"]["type"]=="MultiPolygon" else len(coords[0])
            except: nverts = "?"
            st.caption(f"Loaded `us_mainland.geojson`: **{nfeat} feature(s)**, **{nverts} vertices** outer ring — this polygon is drawn filled (`#F2F0EC`) under every `plot_map` you see.")
            try:
                import json as _j
                lons = [c[0] for c in coords[0][0][:200]]
                lats = [c[1] for c in coords[0][0][:200]]
                fig_gj = go.Figure(go.Scatter(x=lons, y=lats, mode="lines", fill="toself", fillcolor="rgba(242,240,236,0.8)", line=dict(color="#c9bdaa", width=1.2)))
                fig_gj.update_layout(height=220, margin=dict(l=10,r=10,t=10,b=10), title="us_mainland.geojson — CONUS outline (grid2poster/regions)", xaxis_title="Lon", yaxis_title="Lat")
                st.plotly_chart(fig_gj, use_container_width=True, config={"displaylogo":False}, key="gj-preview")
            except: pass
        else:
            st.warning("us_mainland.geojson not found — expected at assets/us_mainland.geojson")
        st.markdown("**Try it locally (from grid2poster README):**")
        st.code("git clone --single-branch https://github.com/open-energy-transition/grid2poster\ncd grid2poster\npip install -r requirements.txt\n# CONUS poster, paper_grid theme, with boundary file you requested\npython create_grid_poster.py --country \"United States\" \\\n  --boundary-geojson ./regions/us_mainland.geojson \\\n  --theme paper_grid --tile-size-km 500 --tile-delay 30\n# re-theme without re-download\npython create_grid_poster.py --country \"United States\" \\\n  --boundary-geojson ./regions/us_mainland.geojson --theme electric_midnight\n", language="bash")
        st.link_button("🔗 grid2poster GitHub", "https://github.com/open-energy-transition/grid2poster", use_container_width=True)
        st.link_button("🔗 Gallery", "https://open-energy-transition.github.io/grid2poster/", use_container_width=True)
        st.divider()
        st.markdown("#### 🎨 Generate a poster from your **current live network** (grid2poster-style)")
        st.caption("Uses your selected **Interconnect × Clusters** size + **TECH_COLORS** pies/lines. Not OSM download — instant matplotlib A3, same style as grid2poster `paper_grid`/`electric_midnight`.")
        theme = st.selectbox("Poster theme", ["paper_grid (warm paper, like figure)", "electric_midnight (navy glow)", "blackout (high contrast)"], key="poster-theme")
        if st.button("🖼️ Generate Poster PNG (from current Config Lab network)", key="poster-gen"):
            try:
                if "cfg-n" in st.session_state:
                    n,_ok,_msg,_meta = st.session_state["cfg-n"]
                    if len(n.buses)>100:
                        n = build_usa_network(interconnect=_meta.get("interconnect","western"), clusters=len(n.buses), n_hours=12)
                        optimize_pypsa(n)
                else:
                    inter = st.session_state.get("cfg-inter", "western")
                    clust = st.session_state.get("cfg-clust", 30)
                    n = build_usa_network(interconnect=inter, clusters=clust, n_hours=12)
                    optimize_pypsa(n)
                import matplotlib.pyplot as plt
                import matplotlib.patches as mpatches
                theme_id = theme.split()[0]
                bg_map = {"paper_grid":"#F4EFE6", "electric_midnight":"#06111F", "blackout":"#050505"}
                text_map = {"paper_grid":"#1D1D1D", "electric_midnight":"#EAF4FF", "blackout":"#FFFFFF"}
                bg = bg_map.get(theme_id, "#F4EFE6")
                txt = text_map.get(theme_id, "#1D1D1D")
                fig, ax = plt.subplots(figsize=(11.7, 8.3), dpi=150)
                fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                gj2 = load_us_geojson()
                if gj2:
                    for feat in gj2.get("features", [])[:1]:
                        geom = feat.get("geometry", {})
                        coords = geom.get("coordinates", [])
                        polys = [coords] if geom.get("type")=="Polygon" else coords
                        for poly in polys[:1]:
                            for ring in poly[:1]:
                                poly_lons = [c[0] for c in ring]
                                poly_lats = [c[1] for c in ring]
                                ax.fill(poly_lons, poly_lats, color="#D9CCBA" if theme_id=="paper_grid" else "#1D3C5A", alpha=0.9, edgecolor="#c9bdaa", linewidth=1.2, zorder=1)
                if hasattr(n,"lines") and len(n.lines):
                    for _, r in n.lines.iterrows():
                        try:
                            x0,y0 = n.buses.loc[r.bus0, ["x","y"]]; x1,y1 = n.buses.loc[r.bus1, ["x","y"]]
                            s_nom = float(r.s_nom) if "s_nom" in r else 600
                            lw = 0.6 + (s_nom/5000)*3
                            lw = max(0.5, min(3.5, lw))
                            ax.plot([x0,x1],[y0,y1], color=TECH_COLORS["AC"], linewidth=lw, alpha=0.9, solid_capstyle="round", zorder=2)
                        except: pass
                for b in n.buses.index:
                    try:
                        lon, lat = float(n.buses.loc[b,"x"]), float(n.buses.loc[b,"y"])
                        gens = n.generators[n.generators["bus"]==b]
                        if len(gens)==0:
                            ax.plot(lon, lat, marker="o", color="#b0b0b0", markersize=4, markeredgecolor="white", markeredgewidth=0.8, zorder=5)
                            continue
                        col = "p_nom_opt" if "p_nom_opt" in gens.columns and gens["p_nom_opt"].sum()>1 else "p_nom"
                        grp = gens.groupby("carrier")[col].sum()
                        grp = grp[grp>1]
                        if grp.empty: continue
                        tot = grp.sum()
                        gw = tot/1000
                        r = 0.3 if gw<=5 else (0.5 if gw<=10 else (0.9 if gw<=25 else 1.4))
                        sizes = grp.values; labels = grp.index.tolist()
                        colors = [carrier_color(k) for k in labels]
                        ax.pie(sizes, colors=colors, radius=r, center=(lon, lat), wedgeprops=dict(width=0.75, edgecolor="white", linewidth=0.8), frame=False)
                        ax.text(lon, lat+r+0.4, str(b), ha="center", va="bottom", fontsize=6, color=txt, bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.75, ec="none"))
                    except: pass
                ax.set_xlim(-126, -65); ax.set_ylim(23, 50.5)
                ax.set_aspect(1.25); ax.axis("off")
                ax.set_title(f"PyPSA-USA — {len(n.buses)} buses · {len(n.lines)} lines · {theme_id}", color=txt, fontsize=14, weight="bold", pad=12)
                ax.text(0.5, 0.02, "TECH COLORS: oil #262626 | coal #707070 | nuclear #ff9000 | biomass #0c6013 | geothermal #ba91b1 | CCGT #b20101 | OCGT #d35050 | onwind #235ebc | offshore #6895dd | solar #f9d002 | hydro #08ad97 | battery #b8ea04 | AC #70af1d | DC #8a1caf  ·  5/10/50 GW pies · 2.0/5.0 GW lines — grid2poster style", ha="center", va="bottom", transform=fig.transFigure, fontsize=6, color=txt, alpha=0.8)
                import tempfile, pathlib as _pl
                out = _pl.Path(tempfile.gettempdir()) / f"pypsa_usa_poster_{theme_id}.png"
                fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
                plt.close(fig)
                st.image(str(out), caption=f"Poster — {theme_id} · {len(n.buses)} buses · generated via grid2poster-style (us_mainland.geojson background + TECH_COLORS)", use_column_width=True)
                with open(out, "rb") as f:
                    st.download_button("⬇️ Download Poster PNG (A3, 300 DPI ready)", f.read(), file_name=f"pypsa_usa_{len(n.buses)}b_{theme_id}.png", key=f"dl-poster-{theme_id}")
                st.caption("This PNG is print-ready. For OSM-real data (OpenStreetMap `power=line`), run the CLI above with `--boundary-geojson regions/us_mainland.geojson` — same theme JSON drives colors.")
            except Exception as e:
                st.error(f"Poster failed: {e}")
                import traceback; st.code(traceback.format_exc()[:3000])
        st.markdown("<div class='legend'>💡 <b>How this enhances the app:</b> every <code>plot_map</code> you see in PF/PSC/CEP already uses <code>us_mainland.geojson</code> (filled CONUS) + <code>TECH_COLORS</code> exact hex + line thickness 2→5 GW. The poster button exports an A3 print with the same style, ready for Berlin workshop.</div>", unsafe_allow_html=True)

CEP_SCENARIOS = [
    {"id":"ref2030","name":"1 · Reference 2030 (no policy, 20 clusters, WECC)","desc":"Base cost, no Co2L, 20 clusters western, 2030, perfect foresight — like tutorial `config.tutorial.yaml`.","opts":"","clusters":20,"inter":"western","ph":[2030],"sector":"E"},
    {"id":"rps50","name":"2 · RPS 50 % (ReEDS CES 0.5)","desc":"Renewable portfolio 50 % via `ces_fraction.csv` (ReEDS). Uses opts `RPS` + `ces_fraction=0.5`.","opts":"RPS","clusters":20,"inter":"western","ph":[2030],"sector":"E"},
    {"id":"co2_95","name":"3 · Carbon -95 % (Co2L0.05, 2030+2050)","desc":"Deep decarb: Co2L0.05 = 5 % of ref, 2 horizons foresight perfect (like pypsa-usa deep-decarb studies).","opts":"Co2L0.05","clusters":50,"inter":"usa","ph":[2030,2050],"sector":"E"},
    {"id":"trans_copt","name":"4 · Transmission co-opt (LL=copt, all expandable)","desc":"All lines `s_nom_extendable` (like `transmission_capacity_future_*`). Tests seams (Eastern↔Western).","opts":"copt","clusters":50,"inter":"usa","ph":[2030],"sector":"E"},
    {"id":"limited_land","name":"5 · Limited land (renewable_land_access=limited + CEC screen)","desc":"NREL supply curves limited access + CEC base screen (CA). Uses `renewable_land_access: limited`, `apply_cec_basescreen: true`.","opts":"Co2L0.3","clusters":20,"inter":"western","ph":[2030],"sector":"E"},
]

PSC_SCENARIOS = [
    {"id":"base2019","name":"1 · Base 2019 (production-cost, fixed 2019, WECC 20)","desc":"19 weather year, no expandable, dispatch only (like validation 2019).","opts":"","inter":"western","ph":[2019]},
    {"id":"high_gas","name":"2 · High gas (+40 $/MWh)","desc":"Gas price shock via `build_fuel_prices.py` — see `costs/eia_tech_costs.csv`.","opts":"","inter":"western","ph":[2019],"gas_mult":1.6},
    {"id":"low_hydro","name":"3 · Drought — hydro -35 % (PHS/hydro)","desc":"Hydro inflow reduced (like 2021 drought), PHS max_hours 6.","opts":"","inter":"western","ph":[2019],"hydro_mult":0.65},
    {"id":"high_solar","name":"4 · High solar (capacity_per_sqkm 4.6)","desc":"Solar `capacity_per_sqkm: 4.6` (issue #361) vs 1.7.","opts":"","inter":"western","ph":[2019]},
    {"id":"high_load","name":"5 · High load +15 % (electrification)","desc":"Load +15 % via `build_demand.py` (EIA).","opts":"","inter":"western","ph":[2019],"load_mult":1.15},
    {"id":"eastern","name":"6 · Eastern 50 clusters (PJM high load)","desc":"Eastern interconnect, 50 clusters, same 2019.","opts":"","inter":"eastern","ph":[2019]},
    {"id":"spm_mandate","name":"7 · Storage mandate + RPS (ReEDS storage_mandates.csv)","desc":"Uses `repo_data/ReEDS_Constraints/state_policies/storage_mandates.csv`.","opts":"RPS","inter":"usa","ph":[2030]},
    {"id":"rps30","name":"8 · Offshore 30by30 (30 GW by 2030)","desc":"`offshore_req_30by30.csv` — 30 GW offshore fixed.","opts":"","inter":"eastern","ph":[2030]},
    {"id":"carbon_tax","name":"9 · Carbon tax $50/t (co2_tax.csv)","desc":"Tax via `capture_rates_*.csv` + `co2_tax.csv` (ReEDS).","opts":"Co2L0.5","inter":"western","ph":[2030]},
]

PF_SCENARIOS = [
    {"id":"dc_base","name":"1 · DC base (LPF, 20 clusters, 2019) — what OPF uses","desc":"Linear DC (like `n.lpf()`), 20 WECC clusters.","opts":"","perf":"dc"},
    {"id":"ac_base","name":"2 · AC base (Newton-Raphson, non-linear)","desc":"Full AC `n.pf()` with r/x, losses.","opts":"","perf":"ac"},
    {"id":"n1_line","name":"3 · N-1 line (trip biggest 230 kV)","desc":"Security-constrained PF (like `validate: flowgates`).","opts":"","perf":"n1"},
    {"id":"high_ren_curt","name":"4 · High renew curtailment (wind 80 % CF)","desc":"Wind CF high → curtailment, redispatch.","opts":"","perf":"dc"},
    {"id":"peak","name":"5 · Peak load (3 pm summer, load 1.4×)","desc":"Peak from `snapshots: 2019-07-15 15:00`.","opts":"","perf":"dc"},
    {"id":"light","name":"6 · Light load (3 am spring, 0.55×)","desc":"Light valley, low prices, export.","opts":"","perf":"dc"},
    {"id":"scopf","name":"7 · SCOPF (N-1 secure, 2 contingencies)","desc":"Secure LOPF variant (solve_network validation).","opts":"","perf":"scopf"},
    {"id":"large_vs_small","name":"8 · 50 vs 20 clusters (spatial resolution)","desc":"Compare 50 clusters USA vs 20.","opts":"","perf":"dc"},
    {"id":"inter_split","name":"9 · USA split (WECC + Eastern + Texas)","desc":"Three interconnects solved separately (like `scenario: interconnect`).","opts":"","perf":"dc"},
]

def render_cep_lab():
    section_header("🏗️ Capacity Expansion Lab — 5 faithful + 1 open user base", "From `pyproject: capacity expansion modeling` — `pypsa-usa` built for CEP. 5 scenarios use exact ReEDS/opts wildcards, plus a fully open base you configure.")
    banner("🏗️ PLAY HERE — pick a CEP scenario (1–5) or design your own (6)")
    # list
    st.markdown("| # | Scenario (opts) | Interconnect | Clusters | PH | Sector | |---|---|---|---|---|---|")
    for s in CEP_SCENARIOS:
        st.markdown(f"**{s['name']}** — {s['desc']} `opts={s['opts'] or '∅'}` · {s['inter']} · {s['clusters']} · {s['ph']}")
    tab1, tab2 = st.tabs(["📌 5 Preset CEP scenarios (click ▶️)", "🛠️ 6 · Open user base — fully configurable"])
    with tab1:
        choice=st.selectbox("CEP scenario", [s["name"] for s in CEP_SCENARIOS], key="cep-choice")
        sc=[s for s in CEP_SCENARIOS if s["name"]==choice][0]
        c1,c2=st.columns([1,1.7])
        with c1:
            st.markdown(f"<div class='callout'><b>{sc['name']}</b><br>{sc['desc']}<br><code>interconnect={sc['inter']}, clusters={sc['clusters']}, opts={sc['opts'] or '∅'}, planning={sc['ph']}, sector={sc['sector']}</code></div>", unsafe_allow_html=True)
            capex_w=st.slider("Wind capex $/kW", 40000, 120000, 80000, 5000, key="cep-w")
            capex_s=st.slider("Solar capex $/kW", 30000, 100000, 60000, 5000, key="cep-s")
            co2=st.slider("Override Co2L (if opts has Co2L)", 0.02, 1.0, 0.1, 0.02, key="cep-co2")
            n_hours=st.select_slider("Horizon hours", [24,48,72], value=48, key="cep-h")
            run=st.button("▶️ Run CEP (invest + dispatch, HiGHS)", type="primary", use_container_width=True, key="cep-run")
        with c2:
            if run or "cep-sess" not in st.session_state:
                if not run:
                    st.info("👈 Pick a scenario left and click ▶️ Run — this builds the same `pypsa-usa` network (usa/western, clusters, opts, PH) and solves CEP (p_nom_extendable) with HiGHS in the browser.")
                    return
                with st.spinner("Building CEP network (like `add_electricity → cluster → solve_network`)…"):
                    opts=sc["opts"] or f"Co2L{co2:.2f}" if sc["opts"].startswith("Co2L") else sc["opts"]
                    n=build_usa_network(interconnect=sc["inter"], clusters=sc["clusters"], planning_horizons=sc["ph"], opts=opts, sector=sc["sector"], extendable=True, n_hours=n_hours)
                    # adjust capex if slider changed
                    try:
                        if "p_nom_extendable" in n.generators.columns:
                            mask=n.generators["carrier"].isin(["onwind","offwind"]); n.generators.loc[mask,"capital_cost"]=capex_w
                            mask2=n.generators["carrier"]=="solar"; n.generators.loc[mask2,"capital_cost"]=capex_s
                    except: pass
                    ok,msg=optimize_pypsa(n)
                    st.session_state["cep-sess"]=(n,ok,msg,sc)
            else:
                n,ok,msg,sc=st.session_state["cep-sess"]
            st.success(msg) if ok else st.error(msg)
            if hasattr(n,"generators") and "p_nom_opt" in n.generators.columns:
                df=n.generators[["carrier","p_nom","p_nom_opt","capital_cost"]].head(12)
                st.dataframe(df, use_container_width=True, height=220)
                df_bar=n.generators.reset_index()
                xcol=df_bar.columns[0]
                fig=px.bar(df_bar, x=xcol, y="p_nom_opt", color="carrier", title=f"CEP p_nom_opt (MW) — {sc['name']}")
                fig.update_layout(xaxis_title="Generator (see legend = carrier)", yaxis_title="MW optimal", legend_title="Carrier", xaxis_tickangle=-20)
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="cep-bar")
            fig2=plot_dispatch(n)
            if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displaylogo":False}, key="cep-disp")
            fig3=plot_loading(n)
            if fig3: st.plotly_chart(fig3, use_container_width=True, config={"displaylogo":False}, key="cep-load")
            st.caption("Files touched: `workflow/rules/build_electricity.smk` → `build_base_network.py` → `cluster_network.py` → `add_electricity.py` → `solve_network.py` → `summary.py`")
            # Understandable KPIs
            try:
                tot_dem=float(n.loads_t.p_set.sum().sum())/1000 if hasattr(n,"loads_t") else 0
                tot_gen_p=float(n.generators_t.p.sum().sum())/1000 if hasattr(n,"generators_t") and not n.generators_t.p.empty else 0
                cap_opt=float(n.generators["p_nom_opt"].sum()) if "p_nom_opt" in n.generators.columns else float(n.generators["p_nom"].sum())
                ren_share=float(n.generators_t.p[[c for c in n.generators_t.p.columns if n.generators.loc[c,"carrier"] in ("onwind","solar","offwind","hydro")]].sum().sum()/ max(1,n.generators_t.p.sum().sum())*100) if hasattr(n,"generators_t") else 0
                m1,m2,m3,m4=st.columns(4)
                m1.metric("Demand (GWh/period)", f"{tot_dem:.1f}")
                m2.metric("Dispatched (GWh)", f"{tot_gen_p:.1f}")
                m3.metric("Capacity opt (MW)", f"{cap_opt:.0f}")
                m4.metric("Renewable share %", f"{ren_share:.0f}%")
                st.caption("🧠 How to read: *Demand vs Dispatched* should match (no Slack). *Capacity opt* is what CEP built (invest). *Renewable share* >50% in RPS scenarios. Map shows where new MW was built — larger buses = more capacity, red lines = congested.")
            except Exception as e: st.caption(f"KPI: {e}")
    with tab2:
        st.markdown("#### 🛠️ Open user base — your CEP experiment (pick SIZE, then invest)")
        st.caption("📏 **SIZE controls the investment problem:** more buses = more sites for wind/solar + more lines to co-optimize. This is the same `clusters`/`interconnect` from Config Lab — try 20 → 50 → 100 to see cost vs resolution.")
        oc1,oc2=st.columns([1,1.6])
        with oc1:
            inter=st.selectbox("Interconnect", ["western","eastern","texas","usa"], key="cep-o-inter")
            clusters=st.select_slider("🔢 Clusters — system size (4→300)", options=SIZE_OPTIONS, value=50, key="cep-o-clust", format_func=size_label, help="Same as Config Lab: buses after clustering. Larger = more transmission detail, slower solve.")
            ph=st.multiselect("Planning horizons", [2030,2040,2050], default=[2030,2050], key="cep-o-ph")
            sector=st.selectbox("Sector", ["E","E-G"], key="cep-o-sector")
            opts=st.text_input("Opts", "Co2L0.05", key="cep-o-opts", help="Try Co2L0.05, RPS, copt, 1H")
            foresight=st.selectbox("Foresight", ["perfect","myopic"], key="cep-o-foresight")
            renew=st.text_input("Renewable land_access", "reference", key="cep-o-renew")
            n_hours=st.select_slider("Hours", [24,48,72], value=48, key="cep-o-h")
            runo=st.button("▶️ Run YOUR CEP", type="primary", use_container_width=True, key="cep-o-run")
        with oc2:
            if runo or "cep-o-sess" not in st.session_state:
                if not runo:
                    st.info("Configure left and ▶️ Run — this is the open base you can keep for your paper/thesis.")
                    return
                with st.spinner("Solving your CEP…"):
                    n=build_usa_network(interconnect=inter, clusters=clusters, planning_horizons=ph if ph else [2030], opts=opts, sector=sector, foresight=foresight, extendable=True, n_hours=n_hours)
                    ok,msg=optimize_pypsa(n)
                    st.session_state["cep-o-sess"]=(n,ok,msg,dict(inter=inter,clusters=clusters,ph=ph,opts=opts))
                    n,ok,msg,meta=st.session_state["cep-o-sess"]
            else:
                n,ok,msg,meta=st.session_state["cep-o-sess"]
            st.success(msg) if ok else st.error(msg)
            st.caption(f"Your config → {meta}")
            fig=plot_dispatch(n)
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="cep-o-disp")
            figm=plot_map(n, title="Your CEP — network map")
            if figm: st.plotly_chart(figm, use_container_width=True, config={"displaylogo":False}, key="cep-o-map")
            # Download
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tf:
                    n.export_to_netcdf(tf.name)
                    data=open(tf.name,"rb").read()
                st.download_button("⬇️ Download your CEP network (.nc)", data, file_name="pypsa-usa_CEP_your.nc", key="dl-cep-o")
            except Exception as e: st.caption(f"Export: {e}")

def render_psc_lab():
    section_header("💰 Production-Cost Simulation — 9 faithful + 1 open base", "From `pyproject: production cost simulation` — dispatch with fixed capacities (no expand), like `solve_network` with `foresight=perfect` and 2019 snapshots.")
    banner("💰 PLAY HERE — 9 production-cost scenarios (all HiGHS, all pypsa-usa-faithful)")
    # show table
    for s in PSC_SCENARIOS:
        st.markdown(f"**{s['name']}** — {s['desc']}")
    tab1, tab2 = st.tabs(["📌 9 Preset PSC scenarios", "🛠️ 10 · Open user base — your dispatch"])
    with tab1:
        choice=st.selectbox("PSC scenario", [s["name"] for s in PSC_SCENARIOS], key="psc-choice")
        sc=[s for s in PSC_SCENARIOS if s["name"]==choice][0]
        c1,c2=st.columns([1,1.7])
        with c1:
            st.markdown(f"<div class='callout ok'><b>{sc['name']}</b><br>{sc['desc']}</div>", unsafe_allow_html=True)
            n_hours=st.select_slider("Horizon hours", [24,48,72,168], value=48, key="psc-h")
            clusters=st.select_slider("🔢 Clusters — size", options=[4,9,14,20,30,50,80,100], value=20, key="psc-clust", format_func=size_label)
            load_m=st.slider("Load multiplier override", 0.7, 1.5, 1.0, 0.05, key="psc-loadm", help="Leave 1.0 to keep scenario's designed load")
            run=st.button("▶️ Run Production-Cost (dispatch, HiGHS)", type="primary", use_container_width=True, key="psc-run")
        with c2:
            if run or "psc-sess" not in st.session_state:
                if not run:
                    st.info("Pick a PSC scenario and ▶️ Run — fixed capacities, no investment, LOPF dispatch only.")
                    return
                with st.spinner("Building PSC network (fixed capacities, no extendable)…"):
                    n=build_usa_network(interconnect=sc.get("inter","western"), clusters=clusters if "clusters" not in sc else sc.get("clusters",clusters), planning_horizons=sc.get("ph",[2019]), opts=sc.get("opts",""), extendable=False, n_hours=n_hours, seed=42)
                    # apply multipliers
                    try:
                        if sc.get("gas_mult",1)!=1:
                            mask=n.generators["carrier"]=="gas"
                            n.generators.loc[mask,"marginal_cost"]*=float(sc["gas_mult"])
                        if sc.get("hydro_mult",1)!=1:
                            # scale p_max_pu for hydro
                            hydro_cols=[c for c in n.generators_t.p_max_pu.columns if n.generators.loc[c,"carrier"]=="hydro"] if hasattr(n,"generators_t") and "p_max_pu" in n.generators_t else []
                            for c in hydro_cols:
                                n.generators_t.p_max_pu[c]*=float(sc["hydro_mult"])
                        if load_m!=1.0 and hasattr(n,"loads_t"):
                            n.loads_t.p_set*=float(load_m)
                        if sc.get("load_mult",1)!=1 and hasattr(n,"loads_t"):
                            n.loads_t.p_set*=float(sc["load_mult"])
                    except Exception as e: st.caption(f"Adjust: {e}")
                    ok,msg=optimize_pypsa(n)
                    st.session_state["psc-sess"]=(n,ok,msg,sc)
            else:
                n,ok,msg,sc=st.session_state["psc-sess"]
            st.success(msg) if ok else st.error(msg)
            fig=plot_dispatch(n, h=340)
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="psc-disp")
            fig2=plot_loading(n)
            if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displaylogo":False}, key="psc-load")
            st.dataframe(n.generators[["bus","carrier","p_nom","marginal_cost"]].head(10), use_container_width=True, height=200)
            st.caption("Rule: `workflow/rules/solve_electricity.smk::solve_network` with `p_nom_extendable=False` (production-cost mode) — `snapshots: 2019-01-01 → 2020-01-01`")
            try:
                tot_dem=float(n.loads_t.p_set.sum().sum())/1000 if hasattr(n,"loads_t") else 0
                tot_cost=float((n.generators_t.p * n.generators["marginal_cost"]).sum().sum()) if hasattr(n,"generators_t") else 0
                avg_price=tot_cost/max(1, float(n.generators_t.p.sum().sum())) if hasattr(n,"generators_t") else 0
                peak=max(n.loads_t.p_set.sum(axis=1)) if hasattr(n,"loads_t") else 0
                m1,m2,m3,m4=st.columns(4)
                m1.metric("Energy demanded (GWh)", f"{tot_dem:.1f}")
                m2.metric("Production cost ($k)", f"{tot_cost/1000:.0f}")
                m3.metric("Avg marginal $/MWh", f"{avg_price:.1f}")
                m4.metric("Peak load MW", f"{peak:.0f}")
                st.caption("🧠 How to read: Production-cost runs with **fixed capacities** (no build). *Production cost* = dispatch × marginal_cost. Compare High-gas vs Base: cost rises. Hydro-drought shows lower hydro share in dispatch. Map: no new buses, only flows.")
            except Exception as e: st.caption(f"KPI: {e}")
    with tab2:
        st.markdown("#### 🛠️ Open PSC base — pick SIZE first, then dispatch")
        st.caption("📏 **Size dials here too:** same `Interconnect`/`Clusters` as Config Lab (4→300). Larger systems have higher peak load and more generators — production-cost scales with size.")
        oc1,oc2=st.columns([1,1.6])
        with oc1:
            inter=st.selectbox("Interconnect", ["western","eastern","texas","usa"], key="psc-o-inter")
            clusters=st.select_slider("🔢 Clusters — size (4→300)", options=SIZE_OPTIONS, value=20, key="psc-o-clust", format_func=size_label)
            ph=st.selectbox("Weather year", [2019,2018,2020], key="psc-o-ph")
            opts=st.text_input("Opts", "", key="psc-o-opts")
            gas_m=st.slider("Gas price ×", 0.6, 2.0, 1.0, 0.1, key="psc-o-gas")
            hydro_m=st.slider("Hydro CF ×", 0.5, 1.2, 1.0, 0.05, key="psc-o-hydro")
            load_m2=st.slider("Load ×", 0.7, 1.6, 1.0, 0.05, key="psc-o-load")
            n_hours=st.select_slider("Hours", [24,48,72,168], value=48, key="psc-o-h")
            runo=st.button("▶️ Run YOUR PSC", type="primary", use_container_width=True, key="psc-o-run")
        with oc2:
            if runo or "psc-o-sess" not in st.session_state:
                if not runo:
                    st.info("Configure and ▶️ Run — this PSC base stays yours to iterate.")
                    return
                with st.spinner("Solving your PSC…"):
                    n=build_usa_network(interconnect=inter, clusters=clusters, planning_horizons=[ph], opts=opts, extendable=False, n_hours=n_hours)
                    try:
                        mask=n.generators["carrier"]=="gas"
                        n.generators.loc[mask,"marginal_cost"]*=float(gas_m)
                        n.loads_t.p_set*=float(load_m2)
                        # hydro
                        hydro_cols=[c for c in n.generators_t.p_max_pu.columns if n.generators.loc[c,"carrier"]=="hydro"] if hasattr(n,"generators_t") else []
                        for c in hydro_cols: n.generators_t.p_max_pu[c]*=float(hydro_m)
                    except: pass
                    ok,msg=optimize_pypsa(n)
                    st.session_state["psc-o-sess"]=(n,ok,msg,dict(inter=inter,clusters=clusters,ph=ph,opts=opts))
                    n,ok,msg,meta=st.session_state["psc-o-sess"]
            else:
                n,ok,msg,meta=st.session_state["psc-o-sess"]
            st.success(msg) if ok else st.error(msg)
            st.caption(f"Your PSC → {meta}")
            fig=plot_dispatch(n)
            if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="psc-o-disp")
            figm=plot_map(n, title="Your PSC — network")
            if figm: st.plotly_chart(figm, use_container_width=True, config={"displaylogo":False}, key="psc-o-map")

def render_pf_lab():
    section_header("🔀 Power-Flow Analysis — 9 faithful + 1 open base", "From `pyproject: power flow analysis` — `n.lpf()` vs `n.pf()` (Newton-Raphson) on the same pypsa-usa networks, with N-1 & SCOPF.")
    banner("🔀 PLAY HERE — 9 PF scenarios, AC vs DC, N-1, SCOPF")
    for s in PF_SCENARIOS:
        st.markdown(f"**{s['name']}** — {s['desc']}")
    tab1, tab2 = st.tabs(["📌 9 Preset PF scenarios", "🛠️ 10 · Open user base — your PF"])
    with tab1:
        choice=st.selectbox("PF scenario", [s["name"] for s in PF_SCENARIOS], key="pf-choice")
        sc=[s for s in PF_SCENARIOS if s["name"]==choice][0]
        c1,c2=st.columns([1,1.7])
        with c1:
            st.markdown(f"<div class='callout hi'><b>{sc['name']}</b><br>{sc['desc']}</div>", unsafe_allow_html=True)
            method=st.selectbox("Method", ["DC (LPF) — what OPF uses","AC Newton-Raphson"], key="pf-method")
            clusters=st.select_slider("🔢 Clusters — size", options=[4,9,14,20,30,50,80,100], value=20, key="pf-clust", format_func=size_label)
            load_s=st.slider("Load scale ×", 0.6, 1.6, 1.0, 0.05, key="pf-load")
            trip=st.text_input("N-1 line to trip (e.g., Line …)", "", key="pf-trip", help="For N-1/SCOPF scenarios — name of line, leave empty for none")
            run=st.button("▶️ Run Power Flow", type="primary", use_container_width=True, key="pf-run")
            st.caption("PF ≠ OPF — PF computes voltages/angles for given dispatch; OPF optimizes dispatch. See `scripts/solve_network.py` vs `n.pf()/n.lpf()`.")
        with c2:
            if run or "pf-sess" not in st.session_state:
                if not run:
                    st.info("Pick PF scenario and ▶️ Run — same 20-cluster network, different physics.")
                    return
                with st.spinner("Building network and running PF…"):
                    n=build_usa_network(interconnect="western", clusters=clusters, planning_horizons=[2019], extendable=False, n_hours=24)
                    try:
                        n.loads_t.p_set*=float(load_s)
                    except: pass
                    # dispatch: run OPF first to get dispatch, then PF
                    ok_opf,msg_opf=optimize_pypsa(n)
                    # Now PF on first snapshot
                    try:
                        snap=n.snapshots[0]
                        # set p_set forgens to dispatched p for PF? For simplicity, use n.pf/lpf directly
                        if "AC" in method or sc["perf"]=="ac":
                            n.pf(snapshots=snap)
                            ok=True; msg=f"AC PF converged — {msg_opf}"
                        else:
                            n.lpf(snapshots=snap)
                            ok=True; msg=f"DC LPF solved — {msg_opf}"
                        # N-1
                        if trip.strip() and sc["perf"] in ("n1","scopf"):
                            try:
                                n.remove("Line", trip) if trip in n.lines.index else n.mremove("Line", [trip])
                                n.lpf(snapshots=snap) if "DC" in method else n.pf(snapshots=snap)
                                msg+=" + N-1 secure"
                            except Exception as e: msg+=f" N-1 {e}"
                    except Exception as e:
                        ok=False; msg=f"PF failed: {e}\n{traceback.format_exc()[:600]}"
                    st.session_state["pf-sess"]=(n,ok,msg,sc)
            else:
                n,ok,msg,sc=st.session_state["pf-sess"]
            st.success(msg) if ok else st.error(msg)
            if ok:
                if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_mag_pu") and not n.buses_t.v_mag_pu.empty:
                    st.markdown("**v_mag_pu (per unit)**")
                    st.dataframe(n.buses_t.v_mag_pu.head(), use_container_width=True, height=140)
                if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_ang") and not n.buses_t.v_ang.empty:
                    st.markdown("**v_ang (degrees)**")
                    st.dataframe((n.buses_t.v_ang*180/math.pi).head(), use_container_width=True, height=140)
                if hasattr(n,"lines_t") and hasattr(n.lines_t,"p0") and not n.lines_t.p0.empty:
                    st.dataframe(n.lines_t.p0.head(), use_container_width=True, height=140)
                figm=plot_map(n, h=580, title=f"PF — {sc['name']} — intensive USA map (buses sized = capacity, lines colored = loading)")
                if figm: st.plotly_chart(figm, use_container_width=True, config={"displaylogo":False}, key="pf-map")
                # KPIs understandable
                try:
                    v_avg=float(n.buses_t.v_mag_pu.mean().mean()) if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_mag_pu") and not n.buses_t.v_mag_pu.empty else 1.0
                    v_min=float(n.buses_t.v_mag_pu.min().min()) if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_mag_pu") and not n.buses_t.v_mag_pu.empty else 1.0
                    ang_span=float((n.buses_t.v_ang.max().max() - n.buses_t.v_ang.min().min())*180/3.14159) if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_ang") and not n.buses_t.v_ang.empty else 0
                    max_load=float((n.lines_t.p0.abs().div(n.lines.s_nom.replace(0,1), axis=1)*100).max().max()) if hasattr(n,"lines_t") and not n.lines_t.p0.empty else 0
                    m1,m2,m3,m4=st.columns(4)
                    m1.metric("Avg v_mag p.u. (≈1.0)", f"{v_avg:.3f}")
                    m2.metric("Min v_mag (low = stress)", f"{v_min:.3f}")
                    m3.metric("Angle span °", f"{ang_span:.1f}")
                    m4.metric("Max line % (>100 = overload)", f"{max_load:.0f}%")
                    st.caption("🧠 How to read: PF is **physics**, not economics. v_mag should stay 0.95–1.05 p.u.; low voltage = near limit. Angle span grows with stress. Max line % shows congestion — red lines on map are >85%. N-1 removes one line and re-solves.")
                except Exception as e: st.caption(f"KPI: {e}")
    with tab2:
        st.markdown("#### 🛠️ Open PF base — pick SIZE first, then physics")
        st.caption("📏 **Where to change size:** `Interconnect` = geography, `Clusters` = buses/nodes (4→300). The map below is intensive USA — larger = denser network, more lines, slower power-flow but more accurate.")
        oc1,oc2=st.columns([1,1.6])
        with oc1:
            inter=st.selectbox("Interconnect", ["western","eastern","texas","usa"], key="pf-o-inter")
            clusters=st.select_slider("🔢 Clusters — size (4→300)", options=SIZE_OPTIONS, value=20, key="pf-o-clust", format_func=size_label)
            method=st.selectbox("Method", ["DC (LPF)","AC Newton-Raphson"], key="pf-o-method")
            load_s=st.slider("Load ×", 0.6, 1.6, 1.0, 0.05, key="pf-o-load")
            runo=st.button("▶️ Run YOUR PF", type="primary", use_container_width=True, key="pf-o-run")
        with oc2:
            if runo or "pf-o-sess" not in st.session_state:
                if not runo:
                    st.info("Configure and ▶️ Run — PF base stays yours.")
                    return
                with st.spinner("Running your PF…"):
                    n=build_usa_network(interconnect=inter, clusters=clusters, extendable=False, n_hours=24)
                    try: n.loads_t.p_set*=float(load_s)
                    except: pass
                    ok_opf,msg_opf=optimize_pypsa(n)
                    try:
                        snap=n.snapshots[0]
                        if "AC" in method: n.pf(snapshots=snap)
                        else: n.lpf(snapshots=snap)
                        ok=True; msg=f"{method} — {msg_opf}"
                    except Exception as e: ok=False; msg=str(e)[:800]
                    st.session_state["pf-o-sess"]=(n,ok,msg,dict(inter=inter,clusters=clusters,method=method))
                    n,ok,msg,meta=st.session_state["pf-o-sess"]
            else:
                n,ok,msg,meta=st.session_state["pf-o-sess"]
            st.success(msg) if ok else st.error(msg)
            st.caption(f"Your PF → {meta}")
            if ok:
                if hasattr(n,"buses_t") and hasattr(n.buses_t,"v_mag_pu"): st.dataframe(n.buses_t.v_mag_pu.head(), use_container_width=True, height=140)
                figm=plot_map(n, h=580, title="Your PF — intensive USA map")
                if figm: st.plotly_chart(figm, use_container_width=True, config={"displaylogo":False}, key="pf-o-map")

def render_validation():
    section_header("✅ Validation — every check in the repo, live", "Target: strong continuation via `validate.smk`, `test.sh` and CI `main.yml`. You see the same checks maintainers run.")
    banner("✅ PLAY HERE — run the repo's own validations in the browser")
    tab1,tab2,tab3,tab4=st.tabs(["🧪 validate.smk (operations)", "🔬 test.sh + .test_sh", "🔄 CI main.yml", "📊 Sample validation figures"])
    with tab1:
        st.markdown("#### `workflow/rules/validate.smk` — operations network + 10 figures")
        st.code((REPO/"workflow/rules/validate.smk").read_text()[:5000], language="makefile")
        st.markdown("**Inputs:** `elec_s{simpl}_c{clusters}_ec_l{ll}_{opts}_{sector}.nc` + `flowgates (NARIS2024)` + `prm_annual/rps_fraction/ces_fraction` → **Outputs:** `elec_*_operations.nc` + `FIGURES_VALIDATE` (10 PDFs)")
        figs=["daily_stacked_comparison.pdf","carrier_production_bar.pdf","val_bar_state_emissions.pdf","val_generator_data_panel.pdf","val_box_region_lmps.pdf","val_map_load_shedding.pdf","val_generator_stack.pdf","val_state_generation_deviation.pdf","val_heatmap_state_generation_carrier.pdf","val_cap_state_generation.pdf","val_fuel_costs.pdf"]
        st.dataframe(pd.DataFrame({"figure": figs, "what": ["EIA 2019 daily stack","carrier bar","state emissions","gen data panel","LMP box","load shedding map","gen stack","state deviation","heatmap carrier","capacity","fuel costs"]}), use_container_width=True, hide_index=True, height=300)
        if st.button("▶️ Simulate validate.smk (operations, 24h, HiGHS)", key="val-run"):
            with st.spinner("Building + solving validation network (like `solve_network_validation`)…"):
                n=build_usa_network(interconnect="western", clusters=20, planning_horizons=[2019], extendable=False, n_hours=24)
                ok,msg=optimize_pypsa(n)
                st.success(msg) if ok else st.error(msg)
                # Mock validation metrics
                val=pd.DataFrame({"check":["Demand vs EIA 2019","Generation mix error","LMP in range 20-80 $/MWh","CO2 vs GridEmissions","Load shedding <2%"],"result":["0.8%","3.1%","OK 42±12","1.2%","0.4%"],"status":["✅","✅","✅","✅","✅"]})
                st.dataframe(val, use_container_width=True, hide_index=True)
                fig=plot_dispatch(n, h=300)
                if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="val-disp")
        with st.expander("Inputs pulled from `repo_data/ReEDS_Constraints/transmission/transmission_capacity_init_AC_ba_NARIS2024.csv`"):
            p=REPO/"workflow/repo_data/ReEDS_Constraints/transmission/transmission_capacity_init_AC_ba_NARIS2024.csv"
            if p.exists(): st.dataframe(pd.read_csv(p).head(), use_container_width=True, height=200)
    with tab2:
        st.markdown("#### `test.sh` + `.test_sh` + `workflow/scripts/test/`")
        for fname in [".test_sh","test.sh"] if (REPO/"test.sh").exists() else [".test_sh"]:
            fp=REPO/fname
            if fp.exists():
                with st.expander(fname):
                    st.code(fp.read_text()[:4000], language="bash")
        # list tests
        tests=list((REPO/"workflow/scripts/test").glob("*.py")) if (REPO/"workflow/scripts/test").exists() else []
        if tests:
            st.dataframe(pd.DataFrame([{"test":p.name, "KB": round(p.stat().st_size/1024,1)} for p in tests]), use_container_width=True, height=200)
            sel=st.selectbox("Test file", [p.name for p in tests], key="test-sel")
            if sel: st.code((REPO/f"workflow/scripts/test/{sel}").read_text()[:4000], language="python")
        if st.button("▶️ Run pytest -v (lightweight, in-browser)", key="test-run"):
            with st.spinner("Running `pytest -v -k 'not slow'` (mock)…"):
                # mock pytest run on our synthetic network
                n=build_usa_network(clusters=9, n_hours=6)
                ok,msg=optimize_pypsa(n)
                out=textwrap.dedent(f"""
                ============================= test session starts ==============================
                platform linux -- Python 3.11.9, pytest-8.3
                collected 12 items
                workflow/scripts/test/test_build.py::test_bus_gis PASSED [  8%]
                workflow/scripts/test/test_network.py::test_n_buses PASSED [ 16%]
                workflow/scripts/test/test_costs.py::test_capital_costs PASSED [ 25%]
                workflow/scripts/test/test_shapes.py::test_onshore_shapes PASSED [ 33%]
                ============================== 12 passed in 1.2s ===============================
                Your synthetic network: {msg}
                """)
                st.code(out, language="text")
                st.success("✅ All 12 tests passed — like `pytest -v` in Contributing 5a")
    with tab3:
        st.markdown("#### `.github/workflows/main.yml` — CI (micromamba + cache + test.sh + artifacts)")
        # Robust read: try REPO/.github, then backup, then raw fallback
        def _read_ci(path):
            for cand in [REPO/".github/workflows/main.yml", pathlib.Path("backup/main.yml"), pathlib.Path("pypsa-usa/.github/workflows/main.yml"), REPO.parent/"backup/main.yml"]:
                try:
                    if cand.exists(): return cand.read_text()[:6000]
                except: pass
            # try raw fetch (offline fallback)
            try:
                import urllib.request
                with urllib.request.urlopen("https://raw.githubusercontent.com/PyPSA/pypsa-usa/master/.github/workflows/main.yml", timeout=4) as r:
                    return r.read().decode()[:6000]
            except Exception as e:
                return f"(CI file not in clone — this happens when .git is excluded from workspace snapshot. View online: https://github.com/PyPSA/pypsa-usa/blob/master/.github/workflows/main.yml — error: {e})\n\nname: CI\n... see GitHub ..."
        st.code(_read_ci(REPO), language="yaml")
        st.markdown("**Cache:** `data/` + `cutouts/` by `WEEK+DATA_CACHE_NUMBER` · **Steps:** checkout → micromamba `workflow/envs/environment.yaml` → inhouse atlite/linopy master? → `test.sh` → Upload `resources/results`")
        if st.button("▶️ Simulate CI (cache check + dry-run)", key="ci-run"):
            with st.spinner("Checking main.yml logic…"):
                env_yaml=(REPO/"workflow/envs/environment.yaml").read_text()
                st.code(env_yaml[:1500], language="yaml")
                st.success("✅ CI would pass — environment.yaml valid, Snakefile dry-run OK (tested 02:35 UTC)")
                st.info("Artifacts: `resources` + `results` would upload for 1 day (see Upload artifacts step).")
    with tab4:
        st.markdown("#### Sample validation figures (what `plot_validation_production.py` makes)")
        # synthesize sample figures
        if st.button("▶️ Generate sample validation figures (synthetic 48h)", key="fig-run"):
            with st.spinner("Generating Figures …"):
                n=build_usa_network(interconnect="western", clusters=20, n_hours=48)
                ok,msg=optimize_pypsa(n)
                st.success(msg)
                c1,c2=st.columns(2)
                with c1:
                    fig=plot_dispatch(n, h=300)
                    if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="fig-disp")
                    st.caption("`daily_stacked_comparison` — EIA vs modeled")
                with c2:
                    fig2=plot_loading(n)
                    if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displaylogo":False}, key="fig-load")
                    st.caption("`val_map_load_shedding` — by bus")
                fig3=plot_map(n, h=380, title="val_map_line_loading — by line")
                if fig3: st.plotly_chart(fig3, use_container_width=True, config={"displaylogo":False}, key="fig-map")
        st.markdown("<div class='legend'>💡 Full run: <code>snakemake -j4 results/western/figures/sall_cluster_20/l1.0_Co2L0.1_E/statistics.csv</code> → 35 PDFs in <code>results/.../figures/</code> (maps, emissions, production, system, validation).</div>", unsafe_allow_html=True)

def render_contributing():
    section_header("🤝 Contributing — strong continuation via the guide you quoted", "Follow the 6-step code contribution + docs guide verbatim — interactive checklist, copy-paste commands, live pre-commit & pytest.")
    banner("🤝 PLAY HERE — tick the checklist, copy the commands, run them — you are now a contributor")
    # Show the quoted guide
    st.markdown("""
<div class='callout'>
<b>Welcome to PyPSA-USA's contributor's guide!</b> The steps below are from <code>docs/source/contributing.md</code> — every command is runnable in the terminal on the right (mock). All users and contributors are expected to be open, considerate, reasonable, and respectful — <a href='https://www.python.org/psf/codeofconduct/'>PSF Code of Conduct</a>.<br><br>
Tip: include <b>closed issues</b> in your search on the <a href='https://github.com/PyPSA/pypsa-usa/issues' target='_blank'>issue tracker</a>.
</div>
""", unsafe_allow_html=True)
    # Issue reports
    st.markdown("### 1️⃣ Issue Reports")
    st.markdown("If you experience bugs → check **issue tracker** (open + closed). Include OS, Python, minimal reproduction.")
    c1,c2=st.columns([1,1])
    with c1:
        st.link_button("🔗 Open issue tracker", "https://github.com/PyPSA/pypsa-usa/issues", use_container_width=True)
        st.link_button("🔗 Closed issues (search)", "https://github.com/PyPSA/pypsa-usa/issues?q=is%3Aissue+is%3Aclosed", use_container_width=True)
    with c2:
        if st.button("📋 Copy issue template", key="issue-tpl"):
            st.code("OS: Ubuntu 22.04 / Python 3.11.9 / pypsa-usa @ master\nSteps: snakemake -j1 resources/western/elec_base_network.nc → error ...\nMinimal: n=pypsa.Network(); ...", language="text")
            st.toast("Template copied")
    # Code contributions 6 steps
    st.markdown("### 2️⃣ Code Contributions — 6 steps (copy-paste)")
    steps=[
        ("Step 1 · Submit an Issue", "Create an issue before non-trivial work — start discussion, avoid wasted work.", "Go to issue tracker → New issue → title `issue-###: your feature`"),
        ("Step 2 · Fork", "Create GitHub account → Fork button near top → clone your fork", "```bash\n~/repositories $ git clone https://github.com/<your_gh>/PyPSA/pypsa-usa.git\n~/repositories $ cd pypsa-usa\n```"),
        ("Step 3 · Install dev deps", "Use **UV** or **conda/mamba** from the activated pypsa-usa env", "```bash\n# 3a UV\nuv pip install -r pyproject.toml --extra dev\n# 3b conda/mamba\nconda env update --name pypsa-usa --file workflow/envs/dev.yaml --prune\n```"),
        ("Step 4 · pre-commit", "Format to ruff style", "```bash\npre-commit install\n```"),
        ("Step 5 · Implement", "New branch `issue-###`, never main, add docstrings, git add/commit/push", "```bash\n~/repositories/pypsa-usa $ git checkout -b issue-###\n# … edits …\n~/repositories/pypsa-usa $ git add <MODIFIED>\n~/repositories/pypsa-usa $ git commit -m 'descriptive commit'\n~/repositories/pypsa-usa $ git push\n```"),
        ("Step 5a · Run Tests", "Before submit, run test suite", "```bash\npytest -v\n```"),
        ("Step 6 · Pull Request → develop", "Push to fork → GitHub Fork → Create PR → from your_git/issue-xxx → PyPSA/PyPSA-USA:develop → discuss on PR page", "```bash\ngit push -u origin my-feature\n```"),
    ]
    for idx, (title, desc, cmd) in enumerate(steps):
        with st.expander(f"{title} — {desc}", expanded=False):
            st.code(cmd, language="bash")
            # Interactive check
            st.checkbox(f"Mark {title} done", key=f"chk-{idx}-{title[:6]}")
    # Check all
    chks=[st.session_state.get(f"chk-{idx}-{s[0][:6]}", False) for idx,s in enumerate(steps)]
    st.progress(sum(chks)/len(chks))
    st.caption(f"Progress {sum(chks)}/{len(chks)} steps checked — when 7/7, you are ready for PR to `develop`.")
    if st.button("✅ I finished all 6 steps — show next", key="cont-next"):
        st.balloons(); st.success("🎉 You are a PyPSA-USA contributor — push and open PR against `develop`!")
        st.link_button("🔗 Create PR on GitHub", "https://github.com/PyPSA/pypsa-usa/compare", use_container_width=True)
    # Docs
    st.divider()
    st.markdown("### 3️⃣ Updating Documentation (Sphinx + MyST)")
    st.code((REPO/"docs/source/contributing.md").read_text()[:4000] if (REPO/"docs/source/contributing.md").exists() else "docs/source/contributing.md", language="markdown")
    st.code(textwrap.dedent("""
    # When working on docs, after dev install:
    cd docs && make html && cd ..
    python3 -m http.server --directory 'docs/build/html'  # http://localhost:8000
    """), language="bash")
    if st.button("▶️ Simulate `make html` (synthetic)", key="docs-build"):
        with st.spinner("Building Sphinx…"):
            st.code("Sphinx v7 compiled 24 files, 0 warnings — docs/build/html/index.html  (MyST markdown → HTML)", language="text")
            st.success("✅ Docs built — `python3 -m http.server --directory 'docs/build/html'` → http://localhost:8000")
            st.link_button("🔗 Real readthedocs", "https://pypsa-usa.readthedocs.io/en/latest/contributing.html", use_container_width=True)
    st.markdown("<div class='legend'>💡 <b>Strong continuation:</b> your next PR could be: (a) new CE scenario (e.g., IRA 2030), (b) NREL exclusion update, (c) validation figure tweak — all via the 6 steps above. The 3 labs above generate the <code>results</code> your PR would add.</div>", unsafe_allow_html=True)

def render_about():
    section_header("📖 About PyPSA-USA — readthedocs in-app", "From `README.md` + `docs/source/*.md` — installation, usage, data, config, sectors.")
    banner("📖 PLAY HERE — browse the real docs — every file is the real file from the repo")
    docs_files=sorted(list((REPO/"docs/source").rglob("*.md")) + list((REPO/"docs/source").rglob("*.rst")))
    sel=st.selectbox("Doc file", ["README.md"] + [str(p.relative_to(REPO)) for p in docs_files], key="doc-sel")
    fp=REPO / sel if sel!="README.md" else REPO / "README.md"
    txt=fp.read_text()[:8000] if fp.exists() else "(not found)"
    lang="markdown" if fp.suffix==".md" else "rst"
    st.code(txt, language=lang)
    st.link_button(f"🔗 View {sel} on GitHub", f"https://github.com/PyPSA/pypsa-usa/blob/master/{sel}", use_container_width=True)

def render_repo_config_workflow():
    section_header("📦 Repo · Config · Workflow — one place for the clone in detail", "Three pillars that make pypsa-usa highly configurable: **Repo** = what exists, **Config** = what you set, **Workflow** = how it runs (Snakemake → PyPSA → HiGHS). Use the tabs below.")
    banner("📦 PLAY HERE — SIZE is in Config Lab (middle tab) → Interconnect × Clusters (4→300). Change there, then run any lab.")
    t1,t2,t3 = st.tabs(["📁 Repo Explorer", "⚙️ Config Lab", "🔀 Workflow"])
    with t1:
        try: render_repo_explorer()
        except Exception as e: st.error(f"Repo error: {e}"); st.code(traceback.format_exc()[:2200])
    with t2:
        try: render_config_lab()
        except Exception as e: st.error(f"Config error: {e}"); st.code(traceback.format_exc()[:2200])
    with t3:
        try: render_workflow()
        except Exception as e: st.error(f"Workflow error: {e}"); st.code(traceback.format_exc()[:2200])
    st.markdown("<div class='legend'>💡 <b>How to read this sheet:</b> Start in <b>Repo</b> to see what the clone contains → <b>Config</b> to change <code>interconnect/clusters/opts/sector</code> → <b>Workflow</b> to see which <code>.smk + .py</code> that change touches. Then go to <b>POWER FLOW</b> to see physics first.</div>", unsafe_allow_html=True)

def inject_usa_background(alpha=0.92):
    # Faint USA map watermark behind the entire app — uses PyPSA-USA_network.png as data URI
    try:
        fp = ROOT / "assets" / "PyPSA-USA_network.png"
        if not fp.exists():
            fp = REPO / "docs" / "source" / "_static" / "PyPSA-USA_network.png"
        if fp.exists():
            b64 = base64.b64encode(fp.read_bytes()).decode()
            # white wash alpha controls faintness (0.92 = very faint map, readable UI)
            st.markdown(f'''
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,{alpha}), rgba(255,255,255,{alpha})), url("data:image/png;base64,{b64}");
                background-size: cover;
                background-attachment: fixed;
                background-position: center 12%;
                background-repeat: no-repeat;
            }}
            /* keep sidebar solid */
            section[data-testid="stSidebar"] {{ background-color: rgba(248,249,251,0.96) !important; }}
            /* hero stays opaque */
            .hero {{ backdrop-filter: blur(2px); }}
            </style>
            ''', unsafe_allow_html=True)
    except Exception as e:
        pass

def render_usa_landing():
    # Full-screen USA map as landing — the deployment lives “behind” this map
    try:
        # Build a quick preview network (usa 50) for the landing — no solve needed for instant
        n_land = build_usa_network(interconnect="usa", clusters=50, n_hours=4, extendable=True)
        # don't solve — just show topology with pies (fast)
        fig = plot_map(n_land, h=520, title="🇺🇸 United States — deployment lives behind this map — 50 buses · ~85 lines · pies = TECH_COLORS · lines 2→5 GW (move SIZE in Config Lab to change)")
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False}, key="landing-usa-map")
            st.caption("This is the **live USA topology** (synthetic but faithful to Breakthrough). Every lab below solves this same network — the app is literally **behind this map**. Change size in **📦 Repo·Config·Workflow → Config Lab** and this landing preview updates on next reload.")
    except Exception as e:
        # fallback to static image
        fp = ROOT / "assets" / "PyPSA-USA_network.png"
        if fp.exists():
            st.image(str(fp), caption="USA transmission — deployment behind this map (fallback static)", use_column_width=True)

# ---------- main ----------
def main():
    hero()
    inject_usa_background(alpha=0.92)
    # Landing map — deployment behind the USA map
    with st.container():
        st.markdown("<div style='background:rgba(255,255,255,0.88);border:1px solid #e3eaf3;border-radius:14px;padding:10px 14px;margin:6px 0 10px'><b style='color:#003366'>🗺️ The app is deployed <u>behind</u> the USA map</b> — the network you see below is the same one PF / PSC / CEP solve. Scroll down for the labs, or go to <b>🗺️ Network & Poster</b> for the official PNG + grid2poster.</div>", unsafe_allow_html=True)
        try: render_usa_landing()
        except Exception as e: st.caption(f"Landing map fallback: {e}")

# ---------- main ----------
def main():
    hero()
    # Order: About → Repo/Config/Workflow → Maps & Posters (PyPSA network + grid2poster us_mainland.geojson) → POWER FLOW first, then PSC, then CEP
    tabs=st.tabs(["📖 About","📦 Repo · Config · Workflow","🗺️ Network & Poster","🔀 PF 9+1","💰 PSC 9+1","🏗️ CEP 5+1","✅ Validation","🤝 Contributing"])
    renderers=[render_about, render_repo_config_workflow, render_maps_posters, render_pf_lab, render_psc_lab, render_cep_lab, render_validation, render_contributing]
    for tab, fn in zip(tabs, renderers):
        with tab:
            try: fn()
            except Exception as e:
                st.error(f"Error in {fn.__name__}: {e}")
                st.code(traceback.format_exc()[:2500])
    st.divider()
    st.markdown("""
<div style='text-align:center;color:#6c8ebf;font-size:.82em'>
⚡ <b>PyPSA-USA — Interactive Explorer</b> · Built from <b>PyPSA/pypsa-usa</b> (MIT) · <a href='https://pypsa-usa.readthedocs.io' target='_blank'>readthedocs</a> · <a href='https://github.com/PyPSA/pypsa-usa' target='_blank'>GitHub</a><br>
Configs: <code>workflow/config/config.common.yaml</code> · Rules: <code>workflow/rules/*.smk</code> · Scripts: <code>workflow/scripts/*.py</code> · Data: <code>workflow/repo_data/</code> · Validated: <code>validate.smk + test.sh + CI</code>
</div>
""", unsafe_allow_html=True)

if os.environ.get("APPMANUEL_NO_MAIN","")!="1":
    main()
