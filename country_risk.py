import requests, pandas as pd, streamlit as st

@st.cache_data(ttl=24*3600)
def fetch_country_risk():
    """
    Return Series: iso3 -> RiskGeo (0 safe → 100 unstable).
    Falls back to empty Series on API error.
    """
    url = (
       "https://api.worldbank.org/v2/country/all/"
       "indicator/PV.POL.STAB"            # correct indicator code
       "?format=json&per_page=20000"      # <-- add per_page
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        # payload expected as [metadata, data_list]; ensure shape
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError("unexpected World Bank payload")

        df = pd.DataFrame(payload[1])  # second element = rows
        df = (
            df[df["date"] == df["date"].max()]
            .loc[:, ["countryiso3code", "value"]]
            .dropna()
        )
        df["RiskGeo"] = (1 - (df["value"] + 2.5) / 5) * 100
        return df.set_index("countryiso3code")["RiskGeo"]

    except Exception as e:
        st.warning(f"World-Bank API error: {e}\nUsing default 50 for RiskGeo.")
        return pd.Series(dtype=float)
