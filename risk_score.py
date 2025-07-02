import pandas as pd, html, bs4, textblob, streamlit as st

# ---------- CONSTANTS ----------
NEG_THRESHOLD  = -0.10          # polarity ≤ –0.10 → negative
UNKNOWN_SCORE  = 50.0           # default when lookup is missing

# ---------- HELPERS ----------
def parse_entries(entries, supplier):
    """
    Convert an RSS 'entries' list into tidy rows with sentiment.
    Returns list of dicts.
    """
    rows = []
    for art in entries:
        raw  = html.unescape(bs4.BeautifulSoup(art["summary"], "lxml").get_text(" "))
        sent = textblob.TextBlob(raw).sentiment.polarity if raw else 0
        rows.append({
            "supplier": supplier,
            "date":    pd.to_datetime(art["published"]),
            "title":   art["title"],
            "sent":    sent,
        })
    return rows

# ---------- COUNTRY-LEVEL MAPS ----------
from country_risk import fetch_country_risk   # iso3 → RiskGeo
from reg_risk     import fetch_reg_risk       # iso3 → RiskReg

# ---------- MAIN AGGREGATION ----------
def compute_scores(
    df: pd.DataFrame,
    supplier_df: pd.DataFrame,
    alpha: float = 0.60,   # headline-sentiment weight
    beta:  float = 0.25,   # geopolitical weight
    gamma: float = 0.15,   # regulatory weight
) -> pd.DataFrame:
    """
    Blend headline sentiment, geopolitical stability, and regulatory burden
    into a single RiskScore (0 = safest, 100 = riskiest).

    Parameters
    ----------
    df : DataFrame  with columns [supplier, sent]
    supplier_df : DataFrame with columns [supplier, country]
    alpha, beta, gamma : weights that must sum to 1.0

    Returns
    -------
    DataFrame sorted by descending RiskScore
    """
    if not abs((alpha + beta + gamma) - 1.0) < 1e-6:
        raise ValueError("alpha + beta + gamma must equal 1.0")

    # 1) SENTIMENT (headline negativity %)
    sent_tbl = (
        df.groupby("supplier")["sent"]
          .apply(lambda x: (x < NEG_THRESHOLD).mean() * 100)
          .to_frame("RiskSent")
    )

    # 2) GEO + REG lookup tables
    geo_map = fetch_country_risk()
    reg_map = fetch_reg_risk()

    supplier_df = supplier_df.copy()
    supplier_df["RiskGeo"] = supplier_df["country"].map(geo_map).fillna(UNKNOWN_SCORE)
    supplier_df["RiskReg"] = supplier_df["country"].map(reg_map).fillna(UNKNOWN_SCORE)

    # 3) Combine & default unknown sentiment to 50
    final = (
        supplier_df
        .join(sent_tbl, on="supplier")
        .fillna({"RiskSent": UNKNOWN_SCORE})
    )

    # 4) Weighted composite
    final["RiskScore"] = (
          alpha * final["RiskSent"]
        + beta  * final["RiskGeo"]
        + gamma * final["RiskReg"]
    ).round(1)

    return final.sort_values("RiskScore", ascending=False)
