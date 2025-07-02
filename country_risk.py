import requests, pandas as pd, streamlit as st

_API = (
    "https://api.worldbank.org/v2/country/all/"
    "indicator/PV.EST?format=json&per_page=20000"
)

@st.cache_data(ttl=24*3600)        # refresh once a day
def fetch_country_risk():
    try:
        data = requests.get(_API, timeout=30).json()[1]          # rows list
        df   = pd.DataFrame(data)
        year = df["date"].max()                                  # latest year
        df   = df[df["date"] == year][["countryiso3code", "value"]].dropna()
        df["RiskGeo"] = (1 - (df["value"] + 2.5) / 5) * 100      # 0 → 100
        return df.set_index("countryiso3code")["RiskGeo"]
    except Exception as e:
        st.warning(f"World-Bank geo fetch failed ({e}); default 50.")
        return pd.Series(dtype=float)
