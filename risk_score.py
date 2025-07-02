import pandas as pd, html, bs4, textblob

NEG_THRESHOLD = -0.10      #   <= –0.10 = clearly negative headline
UNKNOWN_SCORE = 50.0       # when no headlines exist

def parse_entries(entries, supplier):
    """Return list[dict] for one supplier."""
    rows = []
    for art in entries:
        raw  = html.unescape(bs4.BeautifulSoup(art["summary"], "lxml").get_text(" "))
        sent = textblob.TextBlob(raw).sentiment.polarity if raw else 0
        rows.append(
            {
                "supplier": supplier,
                "date": pd.to_datetime(art["published"]),
                "title": art["title"],
                "sent": sent,
            }
        )
    return rows

def compute_scores(df: pd.DataFrame, supplier_list):
    """Return DataFrame with every supplier and a RiskScore column."""
    if df.empty:
        # nobody had headlines
        return pd.DataFrame({"supplier": supplier_list, "RiskScore": UNKNOWN_SCORE})

    scores = (
        df.groupby("supplier")["sent"]
        .apply(lambda x: (x < NEG_THRESHOLD).mean() * 100)
        .reset_index(name="RiskScore")
        .set_index("supplier")
        .reindex(supplier_list)           # keep original order
        .fillna(UNKNOWN_SCORE)
        .reset_index()
        .round(1)
    )
    return scores
