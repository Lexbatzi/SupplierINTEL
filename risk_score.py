import pandas as pd

from country_risk    import fetch_country_risk
from reg_risk        import fetch_reg_risk      # ← NEW

ALPHA = 0.6    # sentiment weight
BETA  = 0.25   # geopolitical weight
GAMMA = 0.15   # regulatory weight   (must add to 1)

def compute_scores(df: pd.DataFrame, supplier_df: pd.DataFrame):
    """Blend three pillars into RiskScore 0–100."""
    # ----- 1) sentiment  -----
    sent_tbl = (
        df.groupby("supplier")["sent"]
          .apply(lambda x: (x < NEG_THRESHOLD).mean() * 100)
          .to_frame("RiskSent")
    )

    # ----- 2) geopolitical -----
    geo_map = fetch_country_risk()
    supplier_df["RiskGeo"] = supplier_df["country"].map(geo_map).fillna(50)

    # ----- 3) regulatory -------
    reg_map = fetch_reg_risk()
    supplier_df["RiskReg"] = supplier_df["country"].map(reg_map).fillna(50)

    final = supplier_df.join(sent_tbl, on="supplier").fillna({"RiskSent": 50})
    final["RiskScore"] = (
          ALPHA * final["RiskSent"]
        + BETA  * final["RiskGeo"]
        + GAMMA * final["RiskReg"]
    ).round(1)

    return final.sort_values("RiskScore", ascending=False)
