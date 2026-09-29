# Deployment behind the USA Map

The app is now visually **behind** the USA transmission map on every deployment:

- **Watermark**: `inject_usa_background(alpha=0.92)` loads `assets/PyPSA-USA_network.png` as base64 `data:image/png` and sets it as `.stApp` background with `linear-gradient(rgba(255,255,255,0.92),...)` + `background-attachment: fixed` + `background-size: cover`. Sidebar stays solid for readability.
- **Landing**: `render_usa_landing()` builds a `usa 50`-bus synthetic network (no solve, instant) and renders it via `plot_map()` (pies 5/10/50 GW, lines 2→5 GW, `us_mainland.geojson` filled) as a 520px hero **before the tabs**. Caption: "The app is deployed behind this map".
- **Poster & static**: `🗺️ Network & Poster` tab still shows the official `PyPSA-USA_network.png` + `user_reference_map.png` + `us_mainland.geojson` + grid2poster theming. That static PNG is also the **social preview** for GitHub/Streamlit.

**Files for deployment:**
- `assets/PyPSA-USA_network.png` (320 KB) → background + landing fallback + `assets/thumbnail.png` + root `thumbnail.png` (for Streamlit Cloud thumbnail)
- `assets/us_mainland.geojson` (395 KB) → filled under every map
- `.streamlit/config.toml` → theme `primary #003366` on `F4EFE6` paper (matches `paper_grid` poster)

**How to set GitHub/Streamlit thumbnail:**
1. GitHub repo → Settings → Social preview → Upload `assets/thumbnail.png`
2. Streamlit Cloud → App settings → Thumbnail (if available) → same file

Every tab now scrolls over the faint USA network — the deployment literally lives **behind the map**.
