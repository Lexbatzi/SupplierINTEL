import pandas as pd
import html, bs4, textblob                   # for sentiment parsing

# ---------- CONSTANTS ----------
NEG_THRESHOLD = -0.10        # polarity ≤ –0.10 → “negative” headline

# weightings must add to 1.0
ALPHA = 0.60    # sentiment weight
BETA  = 0.25    # geopolitical weight
GAMMA = 0.15    # regulatory weight
UNKNOWN_SCORE = 50.0         # default if no data for a pillar

# ---------- HELPERS ----------
def parse_entries(entries, supplier):
    """
    Transform a list of feedparser entries into tidy rows with sentiment.
    Returns list[dict].
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
from country_risk import fetch_country_risk   # RiskGeo  (0 safe → 100 unstable)
from reg_risk     import fetch_reg_risk       # RiskReg  (0 light → 100 heavy)


# ---------- MAIN AGGREGATION ----------
def compute_scores(df: pd.DataFrame, supplier_df: pd.DataFrame) -> pd.DataFrame:
    """
    Blend headline sentiment, geopolitical stability, and regulatory burden
    into a single RiskScore (0 = safest, 100 = riskiest).

    Parameters
    ----------
    df : DataFrame with columns [supplier, sent]
    supplier_df : DataFrame with columns [supplier, country]

    Returns
    -------
    DataFrame with columns
        supplier | country | RiskSent | RiskGeo | RiskReg | RiskScore
    """
    # 1) SENTIMENT ------------------------------------------------------
    sent_tbl = (
        df.groupby("supplier")["sent"]
          .apply(lambda x: (x < NEG_THRESHOLD).mean() * 100)
          .to_frame("RiskSent")
    )

    # 2) GEO + REG look-ups --------------------------------------------
    geo_map = fetch_country_risk()    # iso3 → RiskGeo
    reg_map = fetch_reg_risk()        # iso3 → RiskReg

    supplier_df = supplier_df.copy()
    supplier_df["RiskGeo"] = supplier_df["country"].map(geo_map).fillna(UNKNOWN_SCORE)
    supplier_df["RiskReg"] = supplier_df["country"].map(reg_map).fillna(UNKNOWN_SCORE)

    # 3) Combine & default unknown sentiment to 50 ----------------------
    final = (
        supplier_df
        .join(sent_tbl, on="supplier")
        .fillna({"RiskSent": UNKNOWN_SCORE})
    )

    # 4) Weighted composite score ---------------------------------------
    final["RiskScore"] = (
          ALPHA * final["RiskSent"]
        + BETA  * final["RiskGeo"]
        + GAMMA * final["RiskReg"]
    ).round(1)

    return final.sort_values("RiskScore", ascending=False)

