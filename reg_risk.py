import requests, pandas as pd, streamlit as st

@st.cache_data(ttl=24*3600)
def fetch_reg_risk():
    url = (
        "https://api.worldbank.org/v2/country/all/"
        "indicator/RQ.EST?format=json&per_page=20000"   # ← correct code
    )
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        st.warning("World Bank reg API error – using default 50")
        return pd.Series(dtype=float)

    payload = resp.json()
    if not isinstance(payload, list) or len(payload) < 2:
        st.warning("World Bank reg payload unexpected – using default 50")
        return pd.Series(dtype=float)

    df = pd.DataFrame(payload[1])
    df = (
        df[df["date"] == df["date"].max()]
          .loc[:, ["countryiso3code", "value"]]
          .dropna()
    )
    df["RiskReg"] = (1 - (df["value"] + 2.5) / 5) * 100
    return df.set_index("countryiso3code")["RiskReg"]
