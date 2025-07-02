import requests, pandas as pd, streamlit as st

@st.cache_data(ttl=24*3600)            # refresh once a day
def fetch_reg_risk():
    """Return Series: iso3 → RiskReg  (0 safe → 100 heavy)."""
    url = ("https://api.worldbank.org/v2/country/all/"
           "indicator/CC.REG.QUAL?format=json")
    raw = requests.get(url, timeout=30).json()[1]     # data rows
    df  = (pd.DataFrame(raw)
              .query("date == date.max()")
              .loc[:, ["countryiso3code", "value"]]
              .dropna())
    # High regulatory quality (2.5) → 0 risk ;  Low (-2.5) → 100 risk
    df["RiskReg"] = (1 - (df["value"] + 2.5) / 5) * 100
    return df.set_index("countryiso3code")["RiskReg"]
