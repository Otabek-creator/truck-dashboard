"""
KPI Dashboard — Company Operational Overview
Reads data from 'KPI BOARD.xlsx' and renders an interactive Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme & CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp{background:#F0F2F6;color:#1E293B}
    header[data-testid="stHeader"],footer,#MainMenu{display:none!important;visibility:hidden}
    .block-container{padding-top:.75rem!important;padding-bottom:1rem!important}
    .kpi-card{background:#fff;border-radius:12px;padding:18px 12px;text-align:center;
              box-shadow:0 1px 3px rgba(0,0,0,.08);transition:transform .15s,box-shadow .15s}
    .kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.10)}
    .kpi-label{font-size:12px;font-weight:600;text-transform:uppercase;
               letter-spacing:.6px;color:#64748B;margin-bottom:4px}
    .kpi-number{font-size:30px;font-weight:800;color:#0F172A}
    .section-title{font-size:16px;font-weight:700;color:#334155;
                   margin:24px 0 12px;display:flex;align-items:center;gap:8px}
    [data-testid="stDataFrame"]{border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
    hr{border:0;border-top:1px solid #E2E8F0;margin:28px 0}
    </style>""",
    unsafe_allow_html=True,
)

# ── Palettes ─────────────────────────────────────────────────────────────────
PAL_FLEET   = ["#22C55E", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#94A3B8"]
PAL_TRAILER = ["#22C55E", "#EF4444", "#F59E0B", "#8B5CF6", "#3B82F6", "#06B6D4", "#EC4899", "#94A3B8"]
PAL_CLAIMS  = ["#3B82F6", "#EF4444", "#F59E0B", "#22C55E", "#8B5CF6"]
PAL_TEAM    = ["#3B82F6", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6"]
PAL_HIRING  = ["#22C55E", "#EF4444", "#F59E0B"]
_PAD = {"top": 10, "bottom": 10, "left": 10, "right": 10}


# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    """Load all relevant sheets from the Excel workbook."""
    path = "KPI BOARD.xlsx"
    try:
        xls = pd.ExcelFile(path)
        def _s(name, header=0):
            return pd.read_excel(xls, name, header=header) if name in xls.sheet_names else pd.DataFrame()
        return {
            "fleet": _s("data_fleet"), "trailers": _s("data_trailers"),
            "operations": _s("OPERATIONS"), "data_oper": _s("Data_Oper"),
            "safety": _s("data_safety", header=1), "accidents": _s("data_accidents"),
            "claims": _s("data_claims"), "hiring": _s("data_hiring"),
            "pmservice": _s("data_pmservice"), "load": _s("data_load"),
            "employees": _s("data_employees"),
        }
    except Exception as exc:
        st.error(f"❌ Failed to load data: {exc}")
        return None


# ── Chart helpers ────────────────────────────────────────────────────────────
def _card(label, value, colour="#0F172A"):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-number" style="color:{colour}">{value}</div></div>',
        unsafe_allow_html=True,
    )

def _title(icon, text):
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)

def _hbar(df, x, y, colour="#3B82F6", h=280):
    mx = df[x].max()
    return (
        alt.Chart(df).mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{x}:Q", title=None, scale=alt.Scale(domain=[0, mx * 1.25])),
            y=alt.Y(f"{y}:N", sort="-x", title=None),
            color=alt.value(colour),
            tooltip=[f"{y}:N", f"{x}:Q"],
        ).properties(height=h)
    )

def _vbar(df, x, y, color_col=None, pal=None, h=280):
    enc = {
        "x": alt.X(f"{x}:N", axis=alt.Axis(labelAngle=0), title=None),
        "y": alt.Y(f"{y}:Q", title=None),
        "tooltip": [f"{x}:N", f"{y}:Q"],
    }
    if color_col and pal:
        enc["color"] = alt.Color(f"{color_col}:N", scale=alt.Scale(range=pal), legend=alt.Legend(orient="bottom"))
    else:
        enc["color"] = alt.value("#3B82F6")
    return alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(**enc).properties(height=h)


# ── Main ─────────────────────────────────────────────────────────────────────
data = load_data()
if data is None:
    st.stop()

st.markdown(
    "<h2 style='text-align:center;color:#1E293B;margin:0 0 20px'>📊 Company Operational Dashboard</h2>",
    unsafe_allow_html=True,
)

# ── Row 1: KPI Cards ────────────────────────────────────────────────────────
df_fleet, df_trailers = data["fleet"], data["trailers"]
df_claims, df_accidents = data["claims"], data["accidents"]
df_employees, df_oper = data["employees"], data["operations"]

active_trucks = df_fleet[df_fleet["FLEET STATUS"] == "Active"].shape[0] if "FLEET STATUS" in df_fleet.columns else 0
open_issues = 0
if not df_oper.empty:
    try:
        r = df_oper[df_oper.iloc[:, 0] == "Open"]
        if not r.empty: open_issues = int(r.iloc[0, 1])
    except Exception: pass
open_claims = df_claims[df_claims["STATUS"] == "Open"].shape[0] if "STATUS" in df_claims.columns else 0

for col, (lbl, val, clr) in zip(st.columns(6), [
    ("Active Trucks",   active_trucks,          "#22C55E"),
    ("Total Trailers",  df_trailers.shape[0],   "#3B82F6"),
    ("Open Issues",     open_issues,            "#EF4444"),
    ("Open Claims",     open_claims,            "#F59E0B"),
    ("Total Accidents", df_accidents.shape[0],  "#8B5CF6"),
    ("Employees",       df_employees.shape[0],  "#0EA5E9"),
]):
    with col: _card(lbl, val, clr)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 2: Fleet & Trailers ─────────────────────────────────────────────────
r2a, r2b = st.columns(2)
with r2a:
    _title("🚛", "Fleet Status")
    if "FLEET STATUS" in df_fleet.columns:
        d = df_fleet["FLEET STATUS"].value_counts().reset_index(); d.columns = ["Status", "Count"]
        st.altair_chart(_vbar(d, "Status", "Count", "Status", PAL_FLEET, 320).properties(padding=_PAD))
with r2b:
    _title("📦", "Trailer Status")
    if "Status" in df_trailers.columns:
        d = df_trailers["Status"].value_counts().reset_index(); d.columns = ["Status", "Count"]
        st.altair_chart(_vbar(d, "Status", "Count", "Status", PAL_TRAILER, 320).properties(padding=_PAD))

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 3: Operations & Maintenance ─────────────────────────────────────────
r3a, r3b = st.columns([3, 2])
with r3a:
    _title("🔧", "Urgent Maintenance (Overdue PM)")
    df_pm = data["pmservice"]
    if not df_pm.empty and "Left" in df_pm.columns:
        pm = df_pm.copy(); pm["Left"] = pd.to_numeric(pm["Left"], errors="coerce")
        urgent = pm[pm["Left"] < 0][["Truck Number", "PM Mileage", "Next PM ", "Left", "STATUS"]].sort_values("Left")
        st.dataframe(urgent, column_config={
            "Truck Number": st.column_config.TextColumn("Truck"),
            "Left": st.column_config.NumberColumn("Overdue (mi)", format="%d"),
            "STATUS": st.column_config.TextColumn("PM Status"),
        }, hide_index=True, height=380)
    else: st.info("No PM service data available.")
with r3b:
    _title("⚠️", "Top Issue Categories")
    df_do = data["data_oper"]
    if not df_do.empty and "Issue" in df_do.columns:
        d = df_do["Issue"].value_counts().head(7).reset_index(); d.columns = ["Issue", "Count"]
        st.altair_chart(_hbar(d, "Count", "Issue", "#F59E0B", 380).configure_view(strokeWidth=0).properties(padding={"top": 20, "bottom": 10, "left": 10, "right": 10}))
    else: st.info("No operations issue data.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 4: Safety & Accidents ────────────────────────────────────────────────
r4a, r4b = st.columns(2)
with r4a:
    _title("🚦", "Safety Violations")
    df_sf = data["safety"]
    if not df_sf.empty and "Violation" in df_sf.columns:
        d = df_sf["Violation"].value_counts().head(7).reset_index(); d.columns = ["Violation", "Count"]
        st.altair_chart(_hbar(d, "Count", "Violation", "#EF4444", 340).properties(padding=_PAD))
    else: st.info("No safety data.")
with r4b:
    _title("💥", "Accident — Vehicle Condition")
    if not df_accidents.empty and "Truck Condition" in df_accidents.columns:
        d = df_accidents["Truck Condition"].value_counts().reset_index(); d.columns = ["Condition", "Count"]
        st.altair_chart(_vbar(d, "Condition", "Count", "Condition", ["#22C55E", "#F59E0B", "#EF4444"], 340).properties(padding=_PAD))
    else: st.info("No accident data.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 5: Claims & Dispatch ────────────────────────────────────────────────
r5a, r5b = st.columns(2)
with r5a:
    _title("📋", "Claims by Type")
    if not df_claims.empty and "Type of claim" in df_claims.columns:
        d = df_claims["Type of claim"].value_counts().reset_index(); d.columns = ["Type", "Count"]
        st.altair_chart(_vbar(d, "Type", "Count", "Type", PAL_CLAIMS, 340).properties(padding=_PAD))
    else: st.info("No claims data.")
with r5b:
    _title("🚚", "Dispatch Status by Team")
    df_load = data["load"]
    if not df_load.empty and "Team" in df_load.columns and "Status - UPDATE TEAM" in df_load.columns:
        d = df_load.groupby(["Team", "Status - UPDATE TEAM"]).size().reset_index(name="Count")
        st.altair_chart(
            alt.Chart(d).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("Team:N", axis=alt.Axis(labelAngle=-25), title=None),
                y=alt.Y("Count:Q", title=None),
                color=alt.Color("Status - UPDATE TEAM:N", scale=alt.Scale(range=PAL_TEAM),
                                legend=alt.Legend(orient="bottom", columns=3, title=None)),
                tooltip=["Team:N", "Status - UPDATE TEAM:N", "Count:Q"],
            ).properties(height=340, padding=_PAD)
        )
    else: st.info("No dispatch data.")

st.markdown("<hr>", unsafe_allow_html=True)

# Auto scroll script
components.html(
    """
    <script>
    const scrollSpeed = 1;  // scroll tezligi
    const scrollDelay = 50; // ms

    function autoScroll() {
        window.scrollBy(0, scrollSpeed);

        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight) {
            window.scrollTo(0, 0); // pastga yetganda tepaga qaytadi
        }
    }

    setInterval(autoScroll, scrollDelay);
    </script>
    """,
    height=0,
)