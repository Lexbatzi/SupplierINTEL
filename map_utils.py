import pandas as pd, pathlib, streamlit as st

@st.cache_data
def world_geo_risk():
    """Return DataFrame iso3 | country | RiskGeo from local CSV."""
    path = pathlib.Path(__file__).with_name("world_geo.csv")
    df   = pd.read_csv(path)
    # ensure correct dtypes
    df["iso3"]    = df["iso3"].str.upper()
    df["RiskGeo"] = df["RiskGeo"].astype(float)
    return df
