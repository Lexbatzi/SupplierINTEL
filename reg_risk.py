import requests, pandas as pd, streamlit as st

_API = (
    "https://api.worldbank.org/v2/country/all/"
    "indicator/RQ.EST?format=json&per_page=20000"
)

@st.cache_data(ttl=24*3600)
def fetch_reg_risk():
    try:
        data = requests.get(_API, timeout=30).json()[1]
        df   = pd.DataFrame(data)
        year = df["date"].max()
        df   = df[df["date"] == year][["countryiso3code", "value"]].dropna()
        df["RiskReg"] = (1 - (df["value"] + 2.5) / 5) * 100
        return df.set_index("countryiso3code")["RiskReg"]
    except Exception as e:
        st.warning(f"World-Bank reg fetch failed ({e}); default 50.")
        return pd.Series(dtype=float)
