import requests, pandas as pd, streamlit as st

@st.cache_data(ttl=24*3600)                # cache for one day
def fetch_country_risk():
    url = ("https://api.worldbank.org/v2/country/all/"
           "indicator/LP.PRV.POL.STAB?format=json")
    raw = requests.get(url, timeout=30).json()[1]    # second element = data rows
    df  = pd.DataFrame(raw)
    df  = (df[df["date"] == df["date"].max()]        # latest year
              .loc[:, ["countryiso3code", "value"]]
              .dropna())
    df["RiskGeo"] = (1 - (df["value"] + 2.5) / 5) * 100   # 0 (safe) → 100 (unstable)
    return df.set_index("countryiso3code")["RiskGeo"]
