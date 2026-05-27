"""
RUN — Roman Urdu Normalizer · Demo
CSCS-366 NLP Spring 2026
"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, sys, types

st.set_page_config(
    page_title="RUN — Roman Urdu Normalizer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
* {margin:0!important;padding:0!important}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stDecoration"]{display:none!important}
section[data-testid="stSidebar"]{display:none!important}
.block-container{padding:0!important;max-width:100%!important;margin:0!important}
.stApp,.stApp > div,[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
.element-container,
.stMarkdown,
div[class*="css"]{background:transparent!important;padding:0!important;margin:0!important}
iframe{border:none!important;display:block!important;margin:0!important;padding:0!important}
</style>
""", unsafe_allow_html=True)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner=False)
def load_data():
    stats = {"rules":"7,354","corpus":"220,667","f1":"83.9%","cov":"97.1%"}
    norm_dict = {}
    try:
        p = os.path.join(THIS_DIR, "normalization_dict_final.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                norm_dict = json.load(f)
            stats["rules"] = f"{len(norm_dict):,}"
    except: pass
    frozen = []
    try:
        p2 = os.path.join(THIS_DIR, "frozen_english_v2.json")
        if os.path.exists(p2):
            with open(p2, encoding="utf-8") as f:
                data = json.load(f)
            # could be a dict or a list
            frozen = list(data.keys()) if isinstance(data, dict) else list(data)
    except: pass
    return stats, norm_dict, frozen

stats, norm_dict, frozen_list = load_data()
rules    = stats['rules']
corpus   = stats['corpus']
f1_score = stats['f1']
cov      = stats['cov']
norm_dict_js = json.dumps(norm_dict)
frozen_js    = json.dumps(frozen_list[:3000])

HTML = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

/* ── THEME VARS ── */
[data-theme="light"]{{
  --bg:#f7f9fc; --card:#ffffff; --border:#e2e8f0; --ink:#0f1923; --ink2:#2c3e50;
  --muted:#64748b; --faint:#94a3b8; --thead:#fafbfc;
  --g:#00a67e; --gs:#e8f8f3; --gm:#9adfc8;
  --p:#7c5cbf; --ps:#f1edf9; --pm:#c4b0e8;
  --a:#c97d0a; --as:#fef7e8; --am:#f5c97a;
  --r:#b0558a; --rs:#faeef5; --rm:#e8b8d8;
  --hero-bg:linear-gradient(155deg,#edfaf5 0%,#f5f0fd 45%,#fffbee 100%);
  --shadow:0 2px 12px rgba(0,0,0,.06);
  --toggle-bg:#e2e8f0; --toggle-knob:#ffffff;
  --scrollbar:#e2e8f0;
}}
[data-theme="dark"]{{
  --bg:#0f1117; --card:#1a1f2e; --border:#2a3040; --ink:#e8ecf0; --ink2:#b0bac6;
  --muted:#7a8899; --faint:#4a5568; --thead:#151a27;
  --g:#00c896; --gs:rgba(0,200,150,.12); --gm:rgba(0,200,150,.3);
  --p:#9b7de8; --ps:rgba(155,125,232,.12); --pm:rgba(155,125,232,.3);
  --a:#e8a020; --as:rgba(232,160,32,.12); --am:rgba(232,160,32,.3);
  --r:#d06898; --rs:rgba(208,104,152,.12); --rm:rgba(208,104,152,.3);
  --hero-bg:linear-gradient(155deg,#0d1f1a 0%,#12101f 45%,#1a1508 100%);
  --shadow:0 2px 16px rgba(0,0,0,.4);
  --toggle-bg:#3a4455; --toggle-knob:#e8ecf0;
  --scrollbar:#2a3040;
}}

html{{scroll-behavior:smooth;scrollbar-width:thin;scrollbar-color:var(--scrollbar) transparent;margin:0;padding:0;height:auto}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--ink);line-height:1.5;overflow-x:hidden;transition:background .3s,color .3s;margin:0;padding:0}}

/* ── DARK MODE TOGGLE ── */
.dm-toggle{{
  position:fixed;top:1.2rem;right:1.5rem;z-index:999;
  display:flex;align-items:center;gap:.55rem;
  background:var(--card);border:1px solid var(--border);
  border-radius:999px;padding:.4rem .85rem;cursor:pointer;
  box-shadow:var(--shadow);transition:all .2s;user-select:none;
}}
.dm-toggle:hover{{box-shadow:0 4px 20px rgba(0,0,0,.12);transform:translateY(-1px)}}
.dm-icon{{font-size:.9rem;line-height:1;transition:transform .4s}}
.dm-label{{font-size:.72rem;font-weight:600;color:var(--muted);letter-spacing:.05em}}
.dm-pill{{
  width:32px;height:18px;border-radius:9px;background:var(--toggle-bg);
  position:relative;transition:background .3s;
}}
.dm-pill::after{{
  content:'';position:absolute;top:2px;left:2px;
  width:14px;height:14px;border-radius:50%;
  background:var(--toggle-knob);transition:transform .3s,background .3s;
  box-shadow:0 1px 4px rgba(0,0,0,.2);
}}
[data-theme="dark"] .dm-pill{{background:var(--g)}}
[data-theme="dark"] .dm-pill::after{{transform:translateX(14px)}}
[data-theme="dark"] .dm-icon{{transform:none}}

/* ── HERO ── */
.hero{{
  background:var(--hero-bg);border-bottom:1px solid var(--border);
  padding:2.8rem 5rem 2.5rem;position:relative;overflow:hidden;
  transition:background .3s,border-color .3s;
}}
.orb{{position:absolute;border-radius:50%;filter:blur(70px);pointer-events:none;transition:opacity .3s}}
.o1{{width:420px;height:420px;background:rgba(0,166,126,.13);top:-100px;right:-60px}}
.o2{{width:300px;height:300px;background:rgba(124,92,191,.09);bottom:-80px;left:25%}}
.o3{{width:220px;height:220px;background:rgba(201,125,10,.07);top:20px;left:-40px}}
[data-theme="dark"] .o1{{background:rgba(0,200,150,.08)}}
[data-theme="dark"] .o2{{background:rgba(155,125,232,.06)}}
[data-theme="dark"] .o3{{background:rgba(232,160,32,.05)}}
.hero-inner{{position:relative;z-index:1;display:flex;justify-content:space-between;align-items:flex-start;gap:3rem}}
.hero-left{{flex:1;max-width:700px}}
.wordmark{{
  font-size:5rem;font-weight:900;letter-spacing:-5px;line-height:1;
  background:linear-gradient(135deg,var(--g) 10%,var(--p) 55%,var(--a) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.wordmark-sub{{font-size:.72rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:var(--muted);margin-top:.2rem}}
.hero-desc{{font-size:1rem;color:var(--ink2);line-height:1.8;margin-top:1.1rem;max-width:640px;transition:color .3s}}
.hero-desc strong{{color:var(--ink);font-weight:600}}
.stat-row{{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.4rem}}
.sp{{display:inline-flex;align-items:center;gap:.4rem;padding:.4rem .9rem;border-radius:999px;font-size:.8rem;font-weight:600;border:1px solid;transition:transform .15s,box-shadow .15s,background .3s,color .3s,border-color .3s;cursor:default}}
.sp:hover{{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,.12)}}
.sp-g{{background:var(--gs);color:var(--g);border-color:var(--gm)}}
.sp-a{{background:var(--as);color:var(--a);border-color:var(--am)}}
.sp-p{{background:var(--ps);color:var(--p);border-color:var(--pm)}}
.sp-r{{background:var(--rs);color:var(--r);border-color:var(--rm)}}
.sp-num{{font-size:.95rem;font-weight:800}}
.team-card{{
  background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:1.3rem 1.5rem;min-width:210px;
  box-shadow:var(--shadow);transition:background .3s,border-color .3s,box-shadow .3s;
}}
.tc-course{{font-size:.63rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--faint);margin-bottom:.7rem}}
.tc-name{{font-size:.85rem;font-weight:600;color:var(--ink2);line-height:2.1;transition:color .3s}}
.tc-id{{font-size:.72rem;color:var(--faint);margin-left:.3rem;font-weight:400}}

/* ── SECTIONS ── */
.section{{padding:2.5rem 5rem;border-bottom:1px solid var(--border);transition:border-color .3s}}
.sec-title{{font-size:1.3rem;font-weight:700;color:var(--ink);margin-bottom:.2rem;display:flex;align-items:center;gap:.7rem;transition:color .3s}}
.badge{{font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:3px 10px;border-radius:999px;background:var(--gs);color:var(--g);border:1px solid var(--gm);transition:all .3s}}
.sec-sub{{font-size:.87rem;color:var(--muted);margin-bottom:1.7rem;transition:color .3s}}

/* ── PIPELINE ── */
.pipeline{{display:flex;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--card);box-shadow:var(--shadow);transition:all .3s}}
.ps{{flex:1;padding:1.2rem .7rem;text-align:center;border-right:1px solid var(--border);position:relative;transition:background .2s,border-color .3s;cursor:default}}
.ps:last-child{{border-right:none}}
.ps:hover{{background:var(--gs)}}
.ps.hi{{background:var(--gs)}}
.ps.hi .pn{{color:var(--g)}}
.pnum{{font-size:.58rem;font-weight:700;color:var(--faint);letter-spacing:.1em;margin-bottom:.3rem}}
.pn{{font-size:.77rem;font-weight:700;color:var(--ink);transition:color .3s}}
.pd{{font-size:.62rem;color:var(--muted);margin-top:.2rem;line-height:1.4;transition:color .3s}}
.parr{{position:absolute;right:-8px;top:50%;transform:translateY(-50%);font-size:.65rem;color:var(--border);z-index:2;background:inherit;line-height:1;padding:2px 0}}
.ps:last-child .parr{{display:none}}

/* ── METRIC CARDS ── */
.mgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}}
.mc{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.3rem 1.2rem;transition:transform .2s,box-shadow .2s,background .3s,border-color .3s;cursor:default;box-shadow:var(--shadow)}}
.mc:hover{{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.12)}}
.mv{{font-size:2.1rem;font-weight:800;line-height:1}}
.mt{{display:inline-block;font-size:.6rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:2px 8px;border-radius:999px;margin-top:.3rem;border:1px solid;transition:all .3s}}
.ml{{font-size:.74rem;color:var(--muted);margin-top:.35rem;font-weight:500;transition:color .3s}}

/* ── TABLE ── */
.twrap{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;box-shadow:var(--shadow);transition:all .3s}}
table{{width:100%;border-collapse:collapse;font-size:.87rem}}
thead tr{{background:var(--thead);border-bottom:1px solid var(--border);transition:background .3s}}
th{{font-size:.62rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--faint);padding:.8rem 1rem;text-align:left;transition:color .3s}}
td{{padding:.75rem 1rem;border-bottom:1px solid var(--border);vertical-align:middle;transition:background .3s,border-color .3s,color .3s}}
tr:last-child td{{border-bottom:none}}
tr.run td{{background:var(--gs)}}
tr.run td:first-child{{font-weight:700;color:var(--g);border-left:3px solid var(--g);padding-left:.85rem}}
tr.llm td:first-child{{border-left:3px solid var(--pm);padding-left:.85rem}}
tr.std td:first-child{{border-left:3px solid var(--border);padding-left:.85rem}}
tr:not(.run):hover td{{background:var(--thead)}}
.sn{{font-weight:600;color:var(--ink);display:block;transition:color .3s}}
.sd{{font-size:.74rem;color:var(--muted);transition:color .3s}}
.bw{{display:flex;align-items:center;gap:.6rem}}
.bb{{flex:1;height:7px;background:var(--border);border-radius:4px;overflow:hidden;min-width:80px}}
.bf{{height:100%;border-radius:4px;width:0;transition:width 1.4s cubic-bezier(.4,0,.2,1)}}
.bv{{font-size:.82rem;font-weight:700;width:44px;text-align:right;flex-shrink:0}}

/* ── HANDLES / LIMITS ── */
.twocol{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1.2rem}}
.ic{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.3rem 1.4rem;box-shadow:var(--shadow);transition:all .3s}}
.it{{font-size:.68rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.9rem}}
.expills{{display:flex;flex-wrap:wrap;gap:.4rem}}
.epill{{display:inline-flex;align-items:center;gap:.3rem;background:var(--bg);border:1px solid var(--border);border-radius:7px;padding:.3rem .7rem;font-family:'JetBrains Mono',monospace;font-size:.78rem;transition:border-color .15s,background .15s,color .3s;cursor:default}}
.epill:hover{{border-color:var(--g);background:var(--gs)}}
.ef{{color:var(--a);font-weight:600}}
.et{{color:var(--g);font-weight:600}}
.ea{{color:var(--faint);font-size:.72rem}}
.li{{font-size:.85rem;color:var(--ink2);line-height:2;transition:color .3s}}
.lk{{color:var(--a);font-family:'JetBrains Mono',monospace;font-weight:600;font-size:.8rem}}

/* ── DEMO ── */
.demo-section{{padding:2.5rem 5rem 2rem;border-bottom:none;transition:border-color .3s}}
.ex-btns{{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.2rem}}
.exb{{padding:.4rem .85rem;background:var(--card);border:1px solid var(--border);border-radius:8px;font-family:'Inter',sans-serif;font-size:.78rem;font-weight:500;color:var(--muted);cursor:pointer;transition:all .2s}}
.exb:hover{{border-color:var(--p);color:var(--p);background:var(--ps)}}
.exb.active{{border-color:var(--g);color:var(--g);background:var(--gs);font-weight:600}}
.demo-grid{{display:grid;grid-template-columns:1fr;gap:1rem}}
.dcol{{display:flex;flex-direction:column;gap:.55rem}}
.dlabel{{font-size:.63rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:.4rem;transition:color .3s}}
.dlabel-note{{font-weight:400;color:var(--gm);letter-spacing:0;text-transform:none;font-size:.6rem}}
textarea{{
  width:100%;min-height:100px;padding:.9rem 1rem;
  background:var(--card);border:1.5px solid var(--border);border-radius:12px;
  font-family:'JetBrains Mono',monospace;font-size:.97rem;color:var(--ink);
  line-height:1.85;resize:vertical;outline:none;
  transition:border-color .2s,box-shadow .2s,background .3s,color .3s;
}}
textarea:focus{{border-color:var(--g);box-shadow:0 0 0 3px rgba(0,166,126,.1)}}
textarea::placeholder{{color:var(--faint)}}
.btn-row{{display:flex;gap:.6rem}}
.btn-norm{{
  flex:1;padding:.68rem 1.5rem;background:var(--g);color:#fff;border:none;
  border-radius:10px;font-family:'Inter',sans-serif;font-size:.9rem;font-weight:600;
  cursor:pointer;transition:all .18s;box-shadow:0 3px 14px rgba(0,166,126,.3);
  letter-spacing:.02em;
}}
.btn-norm:hover{{background:#008a68;transform:translateY(-1px);box-shadow:0 6px 22px rgba(0,166,126,.38)}}
.btn-norm:active{{transform:none;box-shadow:0 2px 8px rgba(0,166,126,.28)}}
.btn-norm.spin{{opacity:.75;pointer-events:none}}
.btn-clr{{
  padding:.62rem 1rem;background:var(--card);border:1.5px solid var(--border);
  border-radius:10px;font-family:'Inter',sans-serif;font-size:.85rem;font-weight:500;
  color:var(--muted);cursor:pointer;transition:all .2s;
}}
.btn-clr:hover{{border-color:var(--g);color:var(--g)}}
.lang-tag{{
  display:inline-block;font-size:.6rem;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;padding:2px 9px;border-radius:999px;border:1px solid;
  opacity:0;transition:opacity .3s,transform .3s;transform:translateY(3px);
}}
.lang-tag.show{{opacity:1;transform:translateY(0)}}
.lt-u{{background:var(--gs);color:var(--g);border-color:var(--gm)}}
.lt-e{{background:var(--as);color:var(--a);border-color:var(--am)}}
.lt-m{{background:var(--ps);color:var(--p);border-color:var(--pm)}}
.out-box{{
  min-height:90px;padding:.9rem 1rem;background:var(--card);
  border:1.5px solid var(--border);border-radius:12px;
  font-family:'JetBrains Mono',monospace;font-size:.97rem;
  line-height:1.9;color:var(--ink);word-break:break-word;
  transition:border-color .3s,background .3s,color .3s;
}}
.out-box.lit{{border-color:var(--gm)}}
.out-empty{{color:var(--faint);font-style:italic;font-size:.88rem}}
.tok{{
  background:var(--gs);color:var(--g);border:1px solid var(--gm);
  border-radius:4px;padding:1px 6px;font-weight:600;display:inline-block;
  animation:pop .35s cubic-bezier(.175,.885,.32,1.275) both;
}}
.results-panel{{display:none;grid-template-columns:1fr 1fr;gap:1.5rem;margin-top:1.2rem}}
.results-panel.show{{display:grid}}
.rp-label{{font-size:.63rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:.55rem;display:flex;justify-content:space-between;align-items:center;transition:color .3s}}
.rp-count{{color:var(--g);font-family:'JetBrains Mono',monospace;font-size:.8rem;letter-spacing:0;text-transform:none;font-weight:700}}
.chg-list{{display:flex;flex-direction:column;gap:.3rem}}
.cr{{
  display:flex;align-items:center;gap:.5rem;padding:.48rem .8rem;
  border:1px solid var(--border);border-radius:8px;
  background:var(--card);font-family:'JetBrains Mono',monospace;font-size:.87rem;
  transition:border-color .15s,background .15s,color .3s;
}}
.cr:hover{{border-color:var(--g);background:var(--gs)}}
.cf{{color:var(--a);font-weight:600}}
.ca{{color:var(--faint)}}
.ct{{color:var(--g);font-weight:600}}
.no-chg{{font-size:.87rem;color:var(--g);font-family:'JetBrains Mono',monospace}}
.diff-box{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.2rem 1.4rem;transition:all .3s;
}}
.dkv{{display:flex;justify-content:space-between;align-items:center;font-size:.88rem;padding:.26rem 0}}
.dk{{color:var(--muted);transition:color .3s}}
.dv{{font-weight:700;font-family:'JetBrains Mono',monospace;transition:color .3s}}
.dbar{{height:7px;background:var(--border);border-radius:4px;margin:.6rem 0 .8rem;overflow:hidden;transition:background .3s}}
.dbf{{height:100%;background:linear-gradient(90deg,var(--g),var(--p));border-radius:4px;transition:width .9s cubic-bezier(.4,0,.2,1);width:0}}
.dpct{{font-size:.72rem;color:var(--faint);font-family:'JetBrains Mono',monospace;transition:color .3s}}

/* ── FOOTER ── */
.footer{{
  padding:2rem 5rem 2rem;text-align:center;border-top:1px solid var(--border);
  font-size:.8rem;color:var(--muted);line-height:2;
  transition:border-color .3s,color .3s;
}}
.frun{{
  font-size:1.4rem;font-weight:800;letter-spacing:-1px;
  background:linear-gradient(135deg,var(--g),var(--p),var(--a));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:.3rem;
}}
.footer strong{{color:var(--p);font-weight:600}}

/* ── SCROLL ANIMATIONS ── */
.anim{{
  opacity:0;will-change:opacity,transform;
  transition:opacity .7s cubic-bezier(.4,0,.2,1),transform .7s cubic-bezier(.4,0,.2,1);
}}
/* different entry directions */
.anim-up{{transform:translateY(40px)}}
.anim-left{{transform:translateX(-40px)}}
.anim-right{{transform:translateX(40px)}}
.anim-scale{{transform:scale(.92)}}
.anim-fade{{transform:none}}
.anim.in{{opacity:1!important;transform:none!important}}

/* stagger children */
.stagger > *{{
  opacity:0;transform:translateY(24px);
  transition:opacity .5s cubic-bezier(.4,0,.2,1),transform .5s cubic-bezier(.4,0,.2,1);
}}
.stagger.in > *:nth-child(1){{transition-delay:.05s}}
.stagger.in > *:nth-child(2){{transition-delay:.12s}}
.stagger.in > *:nth-child(3){{transition-delay:.19s}}
.stagger.in > *:nth-child(4){{transition-delay:.26s}}
.stagger.in > *:nth-child(5){{transition-delay:.33s}}
.stagger.in > *:nth-child(6){{transition-delay:.40s}}
.stagger.in > *:nth-child(7){{transition-delay:.47s}}
.stagger.in > *{{opacity:1;transform:none}}

/* pipeline step stagger */
.pipe-stagger > *{{
  opacity:0;transform:translateY(16px) scale(.97);
  transition:opacity .45s ease,transform .45s ease;
}}
.pipe-stagger.in > *{{opacity:1;transform:none}}
.pipe-stagger.in > *:nth-child(1){{transition-delay:.0s}}
.pipe-stagger.in > *:nth-child(2){{transition-delay:.07s}}
.pipe-stagger.in > *:nth-child(3){{transition-delay:.14s}}
.pipe-stagger.in > *:nth-child(4){{transition-delay:.21s}}
.pipe-stagger.in > *:nth-child(5){{transition-delay:.28s}}
.pipe-stagger.in > *:nth-child(6){{transition-delay:.35s}}
.pipe-stagger.in > *:nth-child(7){{transition-delay:.42s}}

/* table row stagger */
.tbl-stagger > *{{opacity:0;transform:translateX(-12px);transition:opacity .4s ease,transform .4s ease}}
.tbl-stagger.in > *{{opacity:1;transform:none}}
.tbl-stagger.in > *:nth-child(1){{transition-delay:.0s}}
.tbl-stagger.in > *:nth-child(2){{transition-delay:.07s}}
.tbl-stagger.in > *:nth-child(3){{transition-delay:.14s}}
.tbl-stagger.in > *:nth-child(4){{transition-delay:.21s}}
.tbl-stagger.in > *:nth-child(5){{transition-delay:.28s}}
.tbl-stagger.in > *:nth-child(6){{transition-delay:.35s}}

/* metric card pop */
.mc-stagger > *{{opacity:0;transform:translateY(20px) scale(.95);transition:opacity .5s ease,transform .5s cubic-bezier(.175,.885,.32,1.275)}}
.mc-stagger.in > *{{opacity:1;transform:none}}
.mc-stagger.in > *:nth-child(1){{transition-delay:.0s}}
.mc-stagger.in > *:nth-child(2){{transition-delay:.09s}}
.mc-stagger.in > *:nth-child(3){{transition-delay:.18s}}
.mc-stagger.in > *:nth-child(4){{transition-delay:.27s}}

@keyframes pop{{from{{opacity:0;transform:scale(.5)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes slideInChg{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
</style>
</head>
<body>

<!-- DARK MODE TOGGLE -->
<div class="dm-toggle" onclick="toggleDark()" title="Toggle dark mode">
  <span class="dm-icon" id="dmIcon">☀️</span>
  <span class="dm-label" id="dmLabel">Light</span>
  <div class="dm-pill"></div>
</div>

<!-- HERO -->
<div class="hero">
  <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
  <div class="hero-inner">
    <div class="hero-left">
      <div class="wordmark anim anim-up" style="transition-delay:.0s">RUN</div>
      <div class="wordmark-sub anim anim-up" style="transition-delay:.08s">Roman Urdu Normalizer</div>
      <p class="hero-desc anim anim-up" style="transition-delay:.16s">
        Pakistani social media is written in <strong>Roman Urdu</strong> — Latin script with wildly
        inconsistent spelling and heavy code-switching with English. RUN is an
        <strong>unsupervised NLP pipeline</strong> that standardizes spelling variants while
        intelligently preserving English text intact.
      </p>
      <div class="stat-row stagger" style="margin-top:1.4rem">
        <span class="sp sp-g"><span class="sp-num">{rules}</span>&thinsp;rules</span>
        <span class="sp sp-a"><span class="sp-num">{corpus}</span>&thinsp;training sentences</span>
        <span class="sp sp-p"><span class="sp-num">{f1_score}</span>&thinsp;F1 score</span>
        <span class="sp sp-r"><span class="sp-num">{cov}</span>&thinsp;token coverage</span>
      </div>
    </div>
    <div class="anim anim-right" style="transition-delay:.24s">
      <div class="team-card">
        <div class="tc-course">CSCS-366 · NLP Spring 2026</div>
        <div class="tc-name">Basima Maham <span class="tc-id">261031499</span></div>
        <div class="tc-name">Soban Khan <span class="tc-id">261039078</span></div>
        <div class="tc-name">Tahreem Fatima <span class="tc-id">261042129</span></div>
        <div style="margin-top:.8rem;font-size:.65rem;color:var(--faint)">CS Department Lahore</div>
      </div>
    </div>
  </div>
</div>

<!-- PIPELINE -->
<div class="section">
  <div class="sec-title anim anim-up">Pipeline Architecture <span class="badge">7 stages</span></div>
  <div class="sec-sub anim anim-up" style="transition-delay:.06s">From raw social media text to normalized output — entirely unsupervised</div>
  <div class="pipeline pipe-stagger">
    <div class="ps"><div class="pnum">01</div><div class="pn">Clean &amp; Tokenize</div><div class="pd">Noise filter · freq vocab</div><span class="parr">›</span></div>
    <div class="ps"><div class="pnum">02</div><div class="pn">English Freeze</div><div class="pd">Lang detect · token lock</div><span class="parr">›</span></div>
    <div class="ps hi"><div class="pnum">03</div><div class="pn">FastText Embed</div><div class="pd">Char n-grams · 100-dim</div><span class="parr">›</span></div>
    <div class="ps"><div class="pnum">04</div><div class="pn">Centroid Cluster</div><div class="pd">Threshold 0.82</div><span class="parr">›</span></div>
    <div class="ps"><div class="pnum">05</div><div class="pn">Hybrid Canon.</div><div class="pd">UrduPhone · edit dist</div><span class="parr">›</span></div>
    <div class="ps hi"><div class="pnum">06</div><div class="pn">Dict Merge</div><div class="pd">{rules} rules learned</div><span class="parr">›</span></div>
    <div class="ps"><div class="pnum">07</div><div class="pn">Inference</div><div class="pd">Sentence-aware output</div></div>
  </div>
</div>

<!-- RESULTS -->
<div class="section">
  <div class="sec-title anim anim-up">Results &amp; Baselines</div>
  <div class="sec-sub anim anim-up" style="transition-delay:.06s">Evaluated on 200 human-annotated held-out sentences · 4 rounds of iterative refinement on 899 dev sentences</div>
  <div class="mgrid mc-stagger">
    <div class="mc"><div class="mv" style="color:var(--g)">83.9%</div><div><span class="mt" style="background:var(--gs);color:var(--g);border-color:var(--gm)">Best F1 overall</span></div><div class="ml">F1 Score</div></div>
    <div class="mc"><div class="mv" style="color:var(--p)">72.3%</div><div><span class="mt" style="background:var(--ps);color:var(--p);border-color:var(--pm)">+31.1pp from v1</span></div><div class="ml">Sentence Precision</div></div>
    <div class="mc"><div class="mv" style="color:var(--a)">100%</div><div><span class="mt" style="background:var(--as);color:var(--a);border-color:var(--am)">Full recall</span></div><div class="ml">Recall</div></div>
    <div class="mc"><div class="mv" style="color:var(--r)">97.1%</div><div><span class="mt" style="background:var(--rs);color:var(--r);border-color:var(--rm)">vs 72.2% manual rules</span></div><div class="ml">Token Coverage</div></div>
  </div>
  <div class="twrap anim anim-scale" style="transition-delay:.1s">
    <table>
      <thead><tr>
        <th style="width:30%">System</th>
        <th style="width:14%;text-align:center">Sent. Prec.</th>
        <th style="width:14%;text-align:center">Tok. Prec.</th>
        <th>F1 Score</th>
      </tr></thead>
      <tbody id="tblBody" class="tbl-stagger"></tbody>
    </table>
  </div>
  <div class="twocol">
    <div class="ic anim anim-left" style="transition-delay:.1s">
      <div class="it" style="color:var(--g)">Handles well</div>
      <div class="expills">
        <span class="epill"><span class="ef">bht</span><span class="ea">→</span><span class="et">bohat</span></span>
        <span class="epill"><span class="ef">nhi</span><span class="ea">→</span><span class="et">nahi</span></span>
        <span class="epill"><span class="ef">yar</span><span class="ea">→</span><span class="et">yaar</span></span>
        <span class="epill"><span class="ef">hy</span><span class="ea">→</span><span class="et">hai</span></span>
        <span class="epill"><span class="ef">or</span><span class="ea">→</span><span class="et">aur</span></span>
        <span class="epill"><span class="ef">rha</span><span class="ea">→</span><span class="et">raha</span></span>
        <span class="epill"><span class="ef">mt</span><span class="ea">→</span><span class="et">mat</span></span>
        <span class="epill"><span class="ef">ap</span><span class="ea">→</span><span class="et">aap</span></span>
        <span class="epill"><span class="ef">kr</span><span class="ea">→</span><span class="et">kar</span></span>
      </div>
      <p style="font-size:.74rem;color:var(--muted);margin-top:.8rem">English sentences preserved intact · Code-switched grammar words normalized</p>
    </div>
    <div class="ic anim anim-right" style="transition-delay:.15s">
      <div class="it" style="color:var(--muted)">Known limitations</div>
      <div class="li"><span class="lk">ha / to / or</span> — appear in both scripts; context-dependent</div>
      <div class="li"><span class="lk">proper nouns</span> — no NER layer; some names affected</div>
      <div class="li"><span class="lk">morphology</span> — gender &amp; tense variants occasionally confused</div>
      <p style="font-size:.7rem;color:var(--faint);margin-top:.6rem">Recall uses RUN's normalizations as gold standard — acknowledged limitation</p>
    </div>
  </div>
</div>

<!-- DEMO -->
<div class="demo-section">
  <div class="sec-title anim anim-up">Try It Live</div>
  <div class="sec-sub anim anim-up" style="transition-delay:.06s">Type any Roman Urdu text — normalization runs in your browser using the trained dictionary</div>
  <div class="ex-btns stagger" id="exBtns">
    <button class="exb" data-t="bhai bht zyada tension mt lo yaar">Roman Urdu</button>
    <button class="exb" data-t="I love how quickly the package was delivered">English text</button>
    <button class="exb" data-t="yaar mujhe seriously tension ho rhi hai exams ki">Code-switched</button>
    <button class="exb" data-t="bohat acha tha yar or bhi ana tha">Pure Urdu variants</button>
  </div>
  <div class="demo-grid anim anim-up" style="transition-delay:.1s">
    <div class="dcol">
      <div class="dlabel">
        Input — Roman Urdu
        <span id="ltag" class="lang-tag"></span>
      </div>
      <textarea id="inp" placeholder="Type Roman Urdu text here…&#10;e.g.  bht accha tha yar"></textarea>
      <div class="btn-row">
        <button class="btn-norm" id="btnN" onclick="doNorm()">Normalize</button>
        <button class="btn-clr" onclick="doClear()">Clear</button>
      </div>
    </div>
    <div class="dcol">
      <div class="dlabel">Output — Normalized <span class="dlabel-note">changed tokens highlighted</span></div>
      <div class="out-box" id="outB"><span class="out-empty">Normalized output will appear here…</span></div>
    </div>
  </div>
  <div class="results-panel" id="resPanel">
    <div>
      <div class="rp-label">Token changes <span class="rp-count" id="rcount"></span></div>
      <div class="chg-list" id="chgList"></div>
    </div>
    <div class="diff-box">
      <div class="rp-label">Diff summary</div>
      <div class="dkv"><span class="dk">Total tokens</span><span class="dv" id="dTot">—</span></div>
      <div class="dkv"><span class="dk">Changed</span><span class="dv" style="color:var(--a)" id="dCh">—</span></div>
      <div class="dkv"><span class="dk">Preserved</span><span class="dv" style="color:var(--g)" id="dKp">—</span></div>
      <div class="dbar"><div class="dbf" id="dbf"></div></div>
      <div class="dpct" id="dpct"></div>
    </div>
  </div>
</div>

<!-- FOOTER -->
<div class="footer anim anim-fade">
  <div class="frun">RUN</div>
  <div><strong>Basima Maham</strong>&nbsp;·&nbsp;<strong>Soban Khan</strong>&nbsp;·&nbsp;<strong>Tahreem Fatima</strong></div>
  <div style="color:var(--faint)">CSCS-366 Natural Language Processing &nbsp;·&nbsp; Spring 2026 &nbsp;·&nbsp; CS Department Lahore</div>
</div>

<script>
const NORM   = {norm_dict_js};
const FROZEN = new Set({frozen_js});

// ── DARK MODE ──────────────────────────────────────────────────────────────────
const html = document.documentElement;
const saved = localStorage.getItem('run-theme');
if(saved) setTheme(saved);

function setTheme(t){{
  html.setAttribute('data-theme',t);
  document.getElementById('dmLabel').textContent = t==='dark'?'Dark':'Light';
  document.getElementById('dmIcon').textContent = t==='dark'?'🌙':'☀️';
  localStorage.setItem('run-theme',t);
}}
function toggleDark(){{
  setTheme(html.getAttribute('data-theme')==='dark'?'light':'dark');
}}

// ── SCROLL ANIMATIONS ──────────────────────────────────────────────────────────
const obs = new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting){{
      e.target.classList.add('in');
      obs.unobserve(e.target);
    }}
  }});
}},{{threshold:0.08,rootMargin:'0px 0px -40px 0px'}});

// Trigger hero immediately
document.querySelectorAll('.hero .anim, .hero .stagger').forEach(el=>{{
  setTimeout(()=>el.classList.add('in'),80);
}});

// Observe all other animated elements
document.querySelectorAll('.anim,.stagger,.pipe-stagger,.mc-stagger,.tbl-stagger').forEach(el=>{{
  if(!el.closest('.hero')) obs.observe(el);
}});

// ── BAR ANIMATIONS ────────────────────────────────────────────────────────────
const barObs = new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting){{
      requestAnimationFrame(()=>{{e.target.style.width=e.target.dataset.w+'%'}});
      barObs.unobserve(e.target);
    }}
  }});
}},{{threshold:0.3}});

// ── TABLE ─────────────────────────────────────────────────────────────────────
const rows=[
  ['Manual Rules','60 hand-crafted rules','75.1%','63.2%',78.0,'var(--muted)','std'],
  ['Edit Distance','Levenshtein similarity','72.5%','70.5%',null,'var(--muted)','std'],
  ['Claude','LLM baseline','73.9%','63.3%',72.3,'var(--p)','llm'],
  ['Gemini','LLM baseline','73.4%','57.5%',78.7,'var(--p)','llm'],
  ['DeepSeek','LLM baseline','72.6%','55.5%',67.5,'var(--p)','llm'],
  ['RUN ★','Ours — unsupervised','72.3%','54.8%',83.9,'var(--g)','run'],
];
const tbody=document.getElementById('tblBody');
rows.forEach(([name,desc,sp,tp,f1,color,cls])=>{{
  const tr=document.createElement('tr');
  tr.className=cls;
  const f1c=f1!=null
    ?`<div class="bw"><div class="bb"><div class="bf" style="background:${{color}}" data-w="${{f1}}"></div></div><span class="bv" style="color:${{color}}">${{f1}}%</span></div>`
    :`<span style="color:var(--faint)">—</span>`;
  tr.innerHTML=`<td><span class="sn">${{name}}</span><span class="sd">${{desc}}</span></td><td style="text-align:center${{cls==='run'?';font-weight:700':''}}">${{sp}}</td><td style="text-align:center${{cls==='run'?';font-weight:700':''}}">${{tp}}</td><td>${{f1c}}</td>`;
  tbody.appendChild(tr);
  document.querySelectorAll('.bf[data-w]').forEach(b=>barObs.observe(b));
}});

// ── LANGUAGE DETECTION ────────────────────────────────────────────────────────
const EN_SIG=new Set(['the','and','but','for','with','from','have','been','will','would',
  'could','should','very','really','actually','good','bad','just','even','also','only',
  'then','than','they','them','their','there','here','when','what','which','you','your',
  'our','my','his','her','its','we','this','that','these','those','not','yes','no',
  'okay','ok','please','thanks','sorry','hello','because','about','after','before',
  'phone','school','college','university','class','exam','test','result','family',
  'friend','life','love','money','today','tomorrow','morning','night','time','quality',
  'received','happy','sad','great','nice','best','new','old','am','are','was','were',
  'do','does','did','go','want','need','look','see','get','give','make','take','come',
  'it','is','in','on','at','he','she','i','love','seriously','quickly','delivered']);
const UR_SIG=new Set(['hai','hain','tha','thi','nahi','bohat','aur','mein','main',
  'ka','ki','ke','ko','se','ne','kya','yeh','woh','aap','hum','bhi','phir','raha','rahi',
  'bht','nhi','yar','hy','rha','rhi','kr','mt','ap','ye','wo','koi','kuch','yaar',
  'tension','ho','hoti','hota']);
const ALWAYS_URDU=new Set(['hai','hain','tha','thi','nahi','bohat','aur','mein','main',
  'ka','ki','ke','ko','se','ne','kya','yeh','woh','aap','hum','bhi','phir','raha','rahi']);

function detectLang(tokens){{
  let en=0,ur=0;
  tokens.forEach(t=>{{
    const tl=t.toLowerCase();
    if(EN_SIG.has(tl)) en++;
    else if(UR_SIG.has(tl)||NORM[tl]) ur++;
  }});
  const tot=en+ur;
  if(!tot) return null;
  const r=en/tot;
  return r>0.68?'en':r<0.35?'ur':'mx';
}}

function normalizeText(text){{
  const tokens=text.trim().split(" ").filter(t=>t.length>0);
  const lang=detectLang(tokens);
  const isEnDom=lang==='en';
  return tokens.map(tok=>{{
    const m=tok.match(/^([^a-zA-Z]*)([a-zA-Z][a-zA-Z']*)([^a-zA-Z]*)$/);
    if(!m) return tok;
    const [,pre,core,suf]=m;
    const tl=core.toLowerCase();
    if(ALWAYS_URDU.has(tl)){{
      const canon=NORM[tl]||tl;
      return pre+(core[0]===core[0].toUpperCase()&&core.length>1?canon[0].toUpperCase()+canon.slice(1):canon)+suf;
    }}
    if(isEnDom&&(FROZEN.has(tl)||EN_SIG.has(tl))) return tok;
    if(NORM[tl]){{
      const canon=NORM[tl];
      const result=(core[0]===core[0].toUpperCase()&&core.length>1&&!/^[A-Z]{{2,}}$/.test(core))
        ?canon[0].toUpperCase()+canon.slice(1):canon;
      return pre+result+suf;
    }}
    return tok;
  }}).join(' ');
}}

// ── LANG BADGE ────────────────────────────────────────────────────────────────
const inp=document.getElementById('inp');
const ltag=document.getElementById('ltag');
let ltimer;
inp.addEventListener('input',()=>{{
  clearTimeout(ltimer);
  ltimer=setTimeout(()=>{{
    const toks=inp.value.trim().split(" ").filter(t=>t.length>0);
    if(!toks.length){{ltag.className='lang-tag';return;}}
    const l=detectLang(toks);
    ltag.className='lang-tag';
    if(l==='en'){{ltag.textContent='English';ltag.classList.add('lt-e','show');}}
    else if(l==='ur'){{ltag.textContent='Roman Urdu';ltag.classList.add('lt-u','show');}}
    else if(l==='mx'){{ltag.textContent='Code-Switched';ltag.classList.add('lt-m','show');}}
    else ltag.classList.remove('show');
  }},280);
}});

// ── EXAMPLE BUTTONS ───────────────────────────────────────────────────────────
document.querySelectorAll('.exb').forEach(btn=>{{
  btn.addEventListener('click',()=>{{
    document.querySelectorAll('.exb').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    inp.value=btn.dataset.t;
    inp.dispatchEvent(new Event('input'));
    document.getElementById('outB').innerHTML='<span class="out-empty">Click Normalize to see the result…</span>';
    document.getElementById('outB').classList.remove('lit');
    document.getElementById('resPanel').classList.remove('show');
  }});
}});

// ── NORMALIZE ─────────────────────────────────────────────────────────────────
function doNorm(){{
  const text=inp.value.trim();
  if(!text) return;
  const btn=document.getElementById('btnN');
  btn.textContent='Normalizing…';btn.classList.add('spin');
  setTimeout(()=>{{
    const norm=normalizeText(text);
    renderResult(text,norm);
    btn.textContent='Normalize';btn.classList.remove('spin');
  }},100);
}}

function renderResult(orig,norm){{
  const outB=document.getElementById('outB');
  const ot=orig.split(" ").filter(t=>t.length>0),nt=norm.split(" ").filter(t=>t.length>0);
  outB.innerHTML=nt.map((n,i)=>{{
    const o=ot[i]||n;
    return o.toLowerCase()!==n.toLowerCase()?`<span class="tok">${{n}}</span>`:n;
  }}).join(' ');
  outB.classList.add('lit');

  const changes=ot.map((o,i)=>{{
    const n=nt[i]||o;
    return o.toLowerCase()!==n.toLowerCase()?{{f:o,t:n}}:null;
  }}).filter(Boolean);
  const n=changes.length;
  document.getElementById('rcount').textContent=n+' change'+(n!==1?'s':'');
  const chgList=document.getElementById('chgList');
  if(n===0){{
    const isEn=detectLang(ot)==='en';
    chgList.innerHTML=`<div class="no-chg">${{isEn?'English sentence — preserved unchanged':'Already canonical — no changes needed'}}</div>`;
  }} else {{
    chgList.innerHTML=changes.map((c,i)=>
      `<div class="cr" style="animation:slideInChg .3s ${{i*.06}}s ease both"><span class="cf">${{c.f}}</span><span class="ca">→</span><span class="ct">${{c.t}}</span></div>`
    ).join('');
  }}
  const total=ot.filter(Boolean).length;
  const pct=total?Math.round(n/total*1000)/10:0;
  document.getElementById('dTot').textContent=total;
  document.getElementById('dCh').textContent=n;
  document.getElementById('dKp').textContent=total-n;
  document.getElementById('dpct').textContent=pct+'% of tokens normalized';
  const dbf=document.getElementById('dbf');
  dbf.style.width='0%';
  requestAnimationFrame(()=>requestAnimationFrame(()=>{{dbf.style.width=pct+'%'}}));
  document.getElementById('resPanel').classList.add('show');
}}

function doClear(){{
  inp.value='';
  ltag.className='lang-tag';
  document.getElementById('outB').innerHTML='<span class="out-empty">Normalized output will appear here…</span>';
  document.getElementById('outB').classList.remove('lit');
  document.getElementById('resPanel').classList.remove('show');
  document.querySelectorAll('.exb').forEach(b=>b.classList.remove('active'));
}}
</script>

</body>
</html>"""

components.html(HTML, height=2700, scrolling=True)