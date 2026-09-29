"""AppTest for PyPSA-USA"""
import os, pathlib
app_path = pathlib.Path(__file__).resolve().parents[1] / "app.py"
os.environ.pop("APPMANUEL_NO_MAIN", None)
os.environ.setdefault("APPMANUEL_SMOKE","1")
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(str(app_path), default_timeout=900)
at.run()
print("exceptions:", len(at.exception))
for e in at.exception:
    print("---- EXCEPTION ----")
    try:
        print(str(e.value)[:4000])
        print("".join([str(x) for x in e.stack_trace][:3])[:2000])
    except:
        import traceback; traceback.print_exc()
for lbl, seq in (("error", at.error), ("warning", at.warning), ("info", at.info), ("success", at.success)):
    for x in seq:
        try: print(f"[{lbl}] {str(x.value)[:700]}")
        except: pass
print(f"\nwidgets: markdown={len(at.markdown)} tabs={len(at.tabs)} plotly={len(at.get('plotly_chart')) if hasattr(at,'get') else 0} buttons={len(at.button)} slider={len(at.slider) if hasattr(at,'slider') else 0} selectbox={len(at.selectbox) if hasattr(at,'selectbox') else 0}")
def _txt(seq):
    out=[]
    for e in seq:
        try: out.append(str(getattr(e,"value","") or getattr(e,"label","") or ""))
        except: continue
    return "\n".join(out)
textos="\n".join([_txt(at.markdown), _txt(at.caption), _txt(at.subheader), _txt(at.header), _txt(at.title), _txt(at.expander), _txt(at.code)])
for w in ("PyPSA-USA","Capacity Expansion","Production-Cost","Power-Flow","Repo Explorer","Config Lab","Workflow","Validation","Contributing","pypsa-usa"):
    print(f" contains {w!r}: {w in textos}")
etiquetas=" | ".join(str(getattr(t,"label","") or "") for t in at.tabs) if at.tabs else ""
print("\npestañas top:", etiquetas or "·")
TABS=["📖 About","📁 Repo Explorer","⚙️ Config Lab","🔀 Workflow","🏗️ CEP 5+1","💰 PSC 9+1","🔀 PF 9+1","✅ Validation","🤝 Contributing"]
fallos=[]
for tab in TABS:
    if tab not in etiquetas: fallos.append(f"missing top tab {tab!r}")
charts=at.get("plotly_chart") if hasattr(at,"get") else []
print(f"plotly figures: {len(charts)}")
if len(at.exception)>0: fallos.append(f"{len(at.exception)} exceptions")
if fallos:
    print("\nFAIL:", fallos)
    import sys; sys.exit(1)
else:
    print("\nAPPTEST OK — 9 top tabs, pypsa-usa clone in detail, CEP 5+1 PSC 9+1 PF 9+1")
