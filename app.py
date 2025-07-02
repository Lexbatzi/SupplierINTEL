# ---------- STREAMLIT FRONT-END -------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px

from gnews_fetch import gnews_articles
from risk_score   import parse_entries, compute_scores

# 0) -----  PAGE CONFIG  ---------------------------------------------
st.set_page_config(page_title="Supplier Risk Monitor", page_icon="📈", layout="wide")

st.title("📈 Supplier-Risk Sentiment Monitor")
st.caption("Google-News headlines ➜ TextBlob sentiment + Geo + Regulatory ➜ Composite Risk Score")

# 1) -----  SUPPLIER LIST SIDEBAR  -----------------------------------
st.sidebar.header("🔧 Supplier list")

uploaded = st.sidebar.file_uploader("CSV with **supplier,country** (ISO-3) columns", type="csv")
if uploaded:
    supplier_df = pd.read_csv(uploaded)
    st.sidebar.success(f"{len(supplier_df)} suppliers loaded from upload.")
else:
    supplier_df = pd.read_csv("suppliers.csv")     # repo default file
    st.sidebar.info(f"Using default list ({len(supplier_df)} suppliers).")

# defensive: ensure both required columns exist
if "country" not in supplier_df.columns:
    supplier_df["country"] = "UNK"

suppliers = supplier_df["supplier"].tolist()

days = st.sidebar.slider("Look-back window (days)", 30, 180, 90, 15)

# 2) -----  FETCH & ANALYSE  -----------------------------------------
bar  = st.progress(0, text="Fetching headlines…")
rows = []

for i, name in enumerate(suppliers, 1):
    rows += parse_entries(gnews_articles(name, days=days), name)
    bar.progress(i / len(suppliers), text=f"Processed {i}/{len(suppliers)} suppliers")

df_raw = pd.DataFrame(rows)
risk_df = compute_scores(df_raw, supplier_df)

# 3) -----  DISPLAY RESULTS  -----------------------------------------
st.subheader("🔎 Composite Risk Scores (%)")
st.dataframe(risk_df.style.format({"RiskScore": "{:.1f}"}), hide_index=True, height=350)

# color-coded bar chart
fig = px.bar(
    risk_df,
    x="supplier",
    y="RiskScore",
    color="RiskScore",
    color_continuous_scale=[(0, "green"), (0.3, "yellow"), (1, "red")],
    range_color=(0, 100),
    title=f"Risk breakdown – last {days} days",
)
fig.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title="Risk %")
st.plotly_chart(fig, use_container_width=True)

with st.expander("📰  Raw headlines"):
    st.dataframe(
        df_raw.sort_values("date", ascending=False).reset_index(drop=True),
        hide_index=True,
        height=300,
    )

st.toast("Done!  You can upload another CSV or adjust the slider to recalc.", icon="✅")
