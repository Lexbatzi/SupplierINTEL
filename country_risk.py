import pandas as pd, pathlib, streamlit as st

@st.cache_data
def fetch_country_risk():
    df = pd.read_csv(pathlib.Path(__file__).with_name("wb_geo.csv"))
    df["RiskGeo"] = (1 - (df["value"] + 2.5) / 5) * 100
    return df.set_index("countryiso3code")["RiskGeo"]
