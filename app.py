# ---------- STREAMLIT FRONT-END -------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px

from gnews_fetch  import gnews_articles
from risk_score   import parse_entries, compute_scores
from country_risk import fetch_country_risk       # only for map legend
from reg_risk     import fetch_reg_risk           # (caches locally)

# ---- PAGE CONFIG ----------------------------------------------------
st.set_page_config(page_title="Supplier Risk Monitor", page_icon="📈", layout="wide")

st.title("📈 Supplier-Risk Sentiment Monitor")
st.caption(
    "Google-News headlines ➜ TextBlob sentiment "
    "+ Geo stability + Regulatory burden ➜ Composite Risk Score"
)

# ---- SUPPLIER LIST SIDEBAR ------------------------------------------
st.sidebar.header("🔧 Supplier list")

uploaded = st.sidebar.file_uploader(
    "CSV with **supplier,country** (ISO-3) columns", type="csv"
)
if uploaded:
    supplier_df = pd.read_csv(uploaded)
    st.sidebar.success(f"{len(supplier_df)} suppliers loaded from upload.")
else:
    supplier_df = pd.read_csv("suppliers.csv")
    st.sidebar.info(f"Using default list ({len(supplier_df)} suppliers).")

# normalise country codes
supplier_df["country"] = (
    supplier_df["country"].astype(str).str.strip().str.upper()
)

suppliers = supplier_df["supplier"].tolist()

days = st.sidebar.slider("Look-back window (days)", 30, 180, 90, 15)

# ---- FETCH & ANALYSE -----------------------------------------------
bar  = st.progress(0, text="Fetching headlines…")
rows = []

for i, name in enumerate(suppliers, 1):
    rows += parse_entries(gnews_articles(name, days=days), name)
    bar.progress(i / len(suppliers), text=f"Processed {i}/{len(suppliers)} suppliers")

df_raw = pd.DataFrame(rows)
risk_df = compute_scores(df_raw, supplier_df)

# ---- DISPLAY: HEADLINE TABLE ---------------------------------------
st.subheader("🔎 Composite Risk Scores (%)")

cols_main = ["supplier", "RiskScore"]
st.dataframe(
    risk_df[cols_main].style.format({"RiskScore": "{:.1f}"}),
    hide_index=True,
    height=350,
)

# full breakdown in expander
with st.expander("See how each score is built"):
    st.dataframe(
        risk_df.style.format(
            {
                "RiskSent": "{:.1f}",
                "RiskGeo": "{:.1f}",
                "RiskReg": "{:.1f}",
                "RiskScore": "{:.1f}",
            }
        ),
        hide_index=True,
        height=350,
    )

# ---- BAR CHART ------------------------------------------------------
fig_bar = px.bar(
    risk_df,
    x="supplier",
    y="RiskScore",
    color="RiskScore",
    color_continuous_scale=[(0, "green"), (0.3, "yellow"), (1, "red")],
    range_color=(0, 100),
    title=f"Risk breakdown – last {days} days",
)
fig_bar.update_layout(
    coloraxis_showscale=False, xaxis_title=None, yaxis_title="Risk %"
)
st.plotly_chart(fig_bar, use_container_width=True)

from map_utils import world_geo_risk
# ---- WORLD MAP ------------------------------------------------------
st.subheader("🌍 Global Political-Stability Risk")

world = world_geo_risk()   # ~240 countries from local CSV
fig_map = px.choropleth(
    world,
    locations="iso3",
    hover_name="country",
    color="RiskGeo",
    color_continuous_scale=[
        [0.0, "#1a9850"],
        [0.3, "#fee08b"],
        [1.0, "#d73027"],
    ],
    range_color=(0, 100),
)
fig_map.update_geos(
    showcountries=True, countrycolor="#444",
    showcoastlines=False, showland=True, landcolor="#202328",
    bgcolor="#0E1117",
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Risk %"),
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
)
st.plotly_chart(fig_map, use_container_width=True)
# ----  RAW HEADLINES -------------------------------------------------
with st.expander("📰  Raw headlines"):
    st.dataframe(
        df_raw.sort_values("date", ascending=False).reset_index(drop=True),
        hide_index=True,
        height=300,
    )
