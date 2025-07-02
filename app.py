import streamlit as st, pandas as pd
from gnews_fetch import gnews_articles
from risk_score  import parse_entries, compute_scores

st.set_page_config(page_title="Supplier Risk Monitor", page_icon="📈")

st.title("📈 Supplier-Risk Sentiment Monitor")
st.caption("Google-News headlines → TextBlob sentiment → % negative = Risk Score")

# --- sidebar supplier upload ---
st.sidebar.header("🔧 Supplier list")
uploaded = st.sidebar.file_uploader("CSV with a 'supplier' column", type="csv")
if uploaded:
    suppliers = pd.read_csv(uploaded)["supplier"].dropna().tolist()
    st.sidebar.success(f"{len(suppliers)} suppliers loaded from upload.")
else:
    suppliers = pd.read_csv("suppliers.csv")["supplier"].tolist()
    st.sidebar.info(f"Using default list ({len(suppliers)} suppliers).")

days = st.sidebar.slider("Look-back window (days)", 30, 180, 90, 15)

# --- fetch + analyse ---
bar = st.progress(0)
rows = []
for i, name in enumerate(suppliers, 1):
    rows += parse_entries(gnews_articles(name, days=days), name)
    bar.progress(i / len(suppliers))

df = pd.DataFrame(rows)
risk_df = compute_scores(df, suppliers)

# --- display ---
st.subheader("Risk scores (%)")
st.dataframe(risk_df, hide_index=True, height=250)

st.subheader("Bar chart")
st.bar_chart(risk_df, x="supplier", y="RiskScore")

with st.expander("See raw headlines"):
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True),
                 hide_index=True, height=300)
