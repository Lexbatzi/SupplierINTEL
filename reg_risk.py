import pandas as pd, pathlib, streamlit as st

@st.cache_data
def fetch_reg_risk():
    df = pd.read_csv(pathlib.Path(__file__).with_name("wb_reg.csv"))
    df["RiskReg"] = (1 - (df["value"] + 2.5) / 5) * 100
    return df.set_index("countryiso3code")["RiskReg"]
