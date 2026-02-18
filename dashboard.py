"""
KPI Dashboard — Company Operational Overview
Reads data from 'KPI BOARD.xlsx' and renders an interactive Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

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
    base = alt.Chart(df)
    bars = base.mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X(f"{x}:Q", title=None, scale=alt.Scale(domain=[0, mx * 1.35])),
        y=alt.Y(f"{y}:N", sort="-x", title=None),
        color=alt.value(colour),
        tooltip=[f"{y}:N", f"{x}:Q"],
    )
    text = base.mark_text(align="left", dx=5, fontSize=14, fontWeight=400, color="#475569").encode(
        x=alt.X(f"{x}:Q"),
        y=alt.Y(f"{y}:N", sort="-x"),
        text=alt.Text(f"{x}:Q"),
    )
    return (bars + text).properties(height=h)

def _vbar(df, x, y, color_col=None, pal=None, h=280):
    base = alt.Chart(df)
    bar_enc = {
        "x": alt.X(f"{x}:N", axis=alt.Axis(labelAngle=0), title=None),
        "y": alt.Y(f"{y}:Q", title=None),
        "tooltip": [f"{x}:N", f"{y}:Q"],
    }
    if color_col and pal:
        bar_enc["color"] = alt.Color(f"{color_col}:N", scale=alt.Scale(range=pal), legend=alt.Legend(orient="bottom"))
    else:
        bar_enc["color"] = alt.value("#3B82F6")
    bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(**bar_enc)
    text = base.mark_text(dy=-10, fontSize=14, fontWeight=400, color="#475569").encode(
        x=alt.X(f"{x}:N"),
        y=alt.Y(f"{y}:Q"),
        text=alt.Text(f"{y}:Q"),
    )
    return (bars + text).properties(height=h)


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
df_oper = data["operations"]

active_trucks = df_fleet[df_fleet["FLEET STATUS"] == "Active"].shape[0] if "FLEET STATUS" in df_fleet.columns else 0
open_issues = 0
if not df_oper.empty:
    try:
        r = df_oper[df_oper.iloc[:, 0] == "Open"]
        if not r.empty: open_issues = int(r.iloc[0, 1])
    except Exception: pass
open_claims = df_claims[df_claims["STATUS"] == "Open"].shape[0] if "STATUS" in df_claims.columns else 0

active_trailers = df_trailers[df_trailers["Status"] == "Active"].shape[0] if "Status" in df_trailers.columns else 0

# Oxirgi 90 kun ichidagi accidentlar
old_accidents = 0
if not df_accidents.empty:
    date_col = None
    for c in df_accidents.columns:
        if "date" in c.lower():
            date_col = c
            break
    if date_col:
        try:
            df_accidents[date_col] = pd.to_datetime(df_accidents[date_col], errors="coerce")
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=90)
            old_accidents = df_accidents[df_accidents[date_col] >= cutoff].shape[0]
        except Exception:
            old_accidents = df_accidents.shape[0]
    else:
        old_accidents = df_accidents.shape[0]
# Oxirgi accidentdan beri necha kun o'tdi
days_since_accident = "N/A"
if not df_accidents.empty and date_col:
    try:
        last_date = df_accidents[date_col].dropna().max()
        if pd.notna(last_date):
            days_since_accident = (pd.Timestamp.now() - last_date).days
    except Exception:
        pass

for col, (lbl, val, clr) in zip(st.columns(6), [
    ("Active Trucks",     active_trucks,       "#22C55E"),
    ("Active Trailers",   active_trailers,     "#3B82F6"),
    ("Open Truck Issues", open_issues,          "#EF4444"),
    ("Open Claims",       open_claims,          "#F59E0B"),
    ("Old Accidents",     old_accidents,        "#8B5CF6"),
    ("Countdown",         f"{days_since_accident} days", "#10B981"),
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
        st.altair_chart(_vbar(d, "Type", "Count", "Type", PAL_CLAIMS, 460).properties(padding=_PAD))
    else: st.info("No claims data.")
with r5b:
    _title("🚚", "Dispatch Status by Team")
    df_load = data["load"]
    if not df_load.empty and "Team" in df_load.columns and "Status - UPDATE TEAM" in df_load.columns:
        d = df_load.groupby(["Team", "Status - UPDATE TEAM"]).size().reset_index(name="Count")
        d.rename(columns={"Status - UPDATE TEAM": "Status"}, inplace=True)
        PAL_DISPATCH = ["#3B82F6", "#22C55E", "#F97316", "#F472B6", "#8B5CF6", "#06B6D4"]
        base = alt.Chart(d)
        bars = base.mark_bar(
            cornerRadiusTopLeft=4, cornerRadiusTopRight=4
        ).encode(
            x=alt.X("Team:N", axis=alt.Axis(labelAngle=0, labelFontSize=12, labelFontWeight=500), title=None),
            y=alt.Y("Count:Q", title=None, stack="zero"),
            color=alt.Color("Status:N",
                scale=alt.Scale(range=PAL_DISPATCH),
                legend=alt.Legend(orient="bottom", columns=3, title=None,
                                 labelFontSize=11, symbolSize=80)),
            tooltip=["Team:N", "Status:N", "Count:Q"],
            order=alt.Order("Count:Q", sort="descending"),
        )
        # Segment midpoint hisoblash — y va y2 oralig'i markazi
        text = base.mark_text(
            fontSize=13, fontWeight=600, color="#fff"
        ).encode(
            x=alt.X("Team:N"),
            y=alt.Y("Count:Q", stack="zero", bandPosition=0.5),
            text=alt.Text("Count:Q"),
            order=alt.Order("Count:Q", sort="descending"),
        ).transform_filter(alt.datum.Count > 1)
        st.altair_chart(
            (bars + text).properties(height=460, padding=_PAD)
                .configure_view(strokeWidth=0)
        )
    else: st.info("No dispatch data.")

st.markdown("<hr>", unsafe_allow_html=True)


# ── Auto-scroll for TV ────────────────────────────────────────────────────────
components.html(
    """
    <script>
        console.log("📺 Auto-scroll script loaded!");

        // ── Dynamik ravishda HAQIQIY scrollable elementni topish ──
        function findScrollableElement() {
            try {
                const doc = window.parent.document;

                // 1-usul: Ma'lum Streamlit selektorlar
                const selectors = [
                    '[data-testid="stMain"]',
                    '[data-testid="stAppViewContainer"]',
                    'section.main',
                    '.main .block-container',
                ];
                for (const sel of selectors) {
                    const el = doc.querySelector(sel);
                    if (el && el.scrollHeight > el.clientHeight + 20) {
                        console.log("✅ Scrollable topildi (selector):", sel);
                        return el;
                    }
                }

                // 2-usul: Barcha elementlarni skanerlash — haqiqiy scrollable ni topish
                const allElements = doc.querySelectorAll('*');
                let bestEl = null;
                let bestDiff = 0;
                for (const el of allElements) {
                    const diff = el.scrollHeight - el.clientHeight;
                    if (diff > 100) {
                        const style = window.parent.getComputedStyle(el);
                        const overflowY = style.overflowY;
                        if (overflowY === 'auto' || overflowY === 'scroll') {
                            if (diff > bestDiff) {
                                bestDiff = diff;
                                bestEl = el;
                            }
                        }
                    }
                }
                if (bestEl) {
                    console.log("✅ Scrollable topildi (scan):", bestEl.tagName, bestEl.className);
                    return bestEl;
                }

                // 3-usul: documentElement yoki body
                if (doc.documentElement.scrollHeight > doc.documentElement.clientHeight + 20) {
                    console.log("✅ Scrollable: documentElement");
                    return doc.documentElement;
                }

                console.log("⚠️ Hech qanday scrollable topilmadi, window ishlatiladi");
                return null;
            } catch(e) {
                console.log("❌ Parent access xatosi:", e.message);
                return null;
            }
        }

        let scrollContainer = null;
        let isPaused = false;
        let retryCount = 0;

        function autoScroll() {
            // Container hali topilmagan bo'lsa, qayta izlash
            if (!scrollContainer) {
                if (retryCount < 30) {
                    retryCount++;
                    scrollContainer = findScrollableElement();
                    if (!scrollContainer) return;
                } else {
                    return; // 30 marta urinib ko'rdi, topilmadi
                }
            }

            if (isPaused) return;

            let scrollTop, scrollHeight, clientHeight;

            // scrollContainer null bo'lsa window.parent dan foydalanish
            if (scrollContainer === null) return;

            scrollTop = scrollContainer.scrollTop;
            scrollHeight = scrollContainer.scrollHeight;
            clientHeight = scrollContainer.clientHeight;

            // Pastga yetganini tekshirish
            if (scrollTop + clientHeight >= scrollHeight - 5) {
                console.log("🛑 Pastga yetdi! scrollTop:", scrollTop, "scrollHeight:", scrollHeight);
                isPaused = true;

                setTimeout(() => {
                    console.log("⬆️ Tepaga qaytish...");
                    scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });

                    setTimeout(() => {
                        console.log("▶️ Davom etish");
                        isPaused = false;
                    }, 2500);
                }, 4000);
            } else {
                scrollContainer.scrollBy(0, 1);
            }
        }

        // 2 soniya kutib boshlash (Streamlit to'liq yuklangan bo'lishi uchun)
        setTimeout(() => {
            console.log("🚀 Auto-scroll boshlandi!");
            window.setInterval(autoScroll, 40);
        }, 2000);
    </script>
    """,
    height=0,
)