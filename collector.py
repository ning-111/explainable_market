"""Simulated news collector for offline testing.

No live feeds are contacted. Each run generates a few fresh sample headlines
from a fixed pool, dated to the last trading day of the seeded price data so
they line up with the charts and the impact analysis.
"""
import random

import db

# (ticker_or_None, sentiment, headline, summary)
SYNTHETIC = [
    ("AAPL", 1, "Analysts lift Apple price targets on stronger services mix",
     "Several brokers raised their Apple price targets, citing the higher-margin services segment now contributing a larger share of revenue."),
    ("NVDA", 1, "Supply-chain checks point to record AI accelerator shipments",
     "Key suppliers report order visibility extending into late 2027, supporting estimates for record accelerator shipments."),
    ("TSLA", -1, "Tesla EU registrations fall for a third straight month",
     "European registration data showed another month of declines for Tesla, intensifying concerns about competition from local EV makers."),
    ("MSFT", 1, "Microsoft expands enterprise AI copilot rollout to new tiers",
     "Microsoft said its AI copilot suite will roll out to mid-market tiers early next year, broadening its monetization funnel."),
    ("COIN", -1, "Stablecoin volumes cool; transaction revenue estimates trimmed",
     "Settlement volumes cooled for a second week, leading analysts to trim Coinbase transaction revenue estimates."),
    ("XOM", -1, "Crude inventories build unexpectedly; energy names slip",
     "A surprise build in US crude inventories pressured oil prices and pulled down energy sector shares in afternoon trade."),
    ("META", 0, "Meta to report quarterly results next week; focus on ad pricing",
     "Investors are watching average ad pricing trends for signals on AI-driven engagement gains heading into the holiday quarter."),
    (None, 0, "Quiet macro calendar keeps indexes range-bound",
     "With no major economic releases, US indexes drifted in a narrow range on light volume ahead of next week's data."),
]

ITEMS_PER_RUN = 2


def collect():
    """Run one simulated collection pass; returns the number of new items."""
    conn = db.get_conn()
    inserted = 0
    try:
        row = conn.execute("SELECT MAX(date) FROM prices").fetchone()
        published = row[0] if row else "2026-10-29"
        pool = [row for row in SYNTHETIC
                if not conn.execute("SELECT 1 FROM news WHERE headline = ?",
                                    (row[2],)).fetchone()]
        for ticker, sentiment, headline, summary in random.sample(
                pool, k=min(ITEMS_PER_RUN, len(pool))):
            conn.execute(
                "INSERT INTO news(headline, summary, source, published, ticker,"
                " sentiment, magnitude, is_market) VALUES (?,?,?,?,?,?,?,?)",
                (headline, summary, "Demo Collector", published, ticker,
                 sentiment, 0.0, 0))
            inserted += 1
        conn.commit()
    finally:
        conn.close()
    return inserted
