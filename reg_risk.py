import requests, pandas as pd, streamlit as st

@st.cache_data(ttl=24*3600)
def fetch_reg_risk():
    """
    World-Bank ‘Regulatory Quality’ index  →  RiskReg  (0 light → 100 heavy).
    Falls back to empty Series on error.
    """
    url = (
        "https://api.worldbank.org/v2/country/all/"
        "indicator/CC.REG.QUAL?format=json"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        # Expect [metadata, data]; guard against bad shapes
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError("unexpected World Bank payload")

        df = pd.DataFrame(payload[1])
        df = (
            df[df["date"] == df["date"].max()]
            .loc[:, ["countryiso3code", "value"]]
            .dropna()
        )
        df["RiskReg"] = (1 - (df["value"] + 2.5) / 5) * 100
        return df.set_index("countryiso3code")["RiskReg"]

    except Exception as e:
        st.warning(f"World-Bank REG-QUAL API error: {e}. Using default 50.")
        return pd.Series(dtype=float)
