"""Deterministic demo data: symbols, 120 trading days of prices with
news-driven shocks engineered into the series, news items, and a demo user.

The price shocks are generated FROM the news plan, so every big move in the
charts is genuinely explained by a news event — that is the whole point of
the "explainable market" demo.
"""
import hashlib
import random
import zlib
from datetime import date, timedelta


def stable_seed(text: str) -> int:
    """Process-independent hash so re-seeding always produces the same data."""
    return zlib.crc32(text.encode())

TRADING_DAYS = 120
LAST_DAY = date(2026, 10, 29)  # last seeded trading day

# ticker, name, sector, base price
SYMBOLS = [
    ("AAPL",  "Apple Inc.",          "Technology",  262.0),
    ("MSFT",  "Microsoft Corp.",     "Technology",  488.0),
    ("NVDA",  "NVIDIA Corp.",        "Semiconductors", 198.0),
    ("AMD",   "Advanced Micro Devices", "Semiconductors", 236.0),
    ("TSLA",  "Tesla Inc.",          "Automotive",  428.0),
    ("AMZN",  "Amazon.com Inc.",     "Consumer Discretionary", 241.0),
    ("GOOGL", "Alphabet Inc.",       "Technology",  208.0),
    ("META",  "Meta Platforms Inc.", "Technology",  694.0),
    ("NFLX",  "Netflix Inc.",        "Media",      1142.0),
    ("JPM",   "JPMorgan Chase & Co.", "Financials", 305.0),
    ("XOM",   "Exxon Mobil Corp.",   "Energy",      117.0),
    ("COIN",  "Coinbase Global Inc.", "Crypto",     318.0),
]

# days_ago=0 means the shock lands on the last trading day.
# (days_ago, ticker_or_None_for_market, sentiment, magnitude_pct, headline, summary, source)
NEWS = [
    (0, "AAPL", 1, 3.6, "Apple services revenue hits all-time high, buyback expanded",
     "Apple posted record services revenue and expanded its share buyback program by $90B, lifting the stock to session highs.",
     "Bloomberg"),
    (0, "TSLA", -1, 4.8, "Tesla margins miss estimates as price cuts bite",
     "Tesla's automotive gross margin fell short of consensus as continued price cuts outweighed record deliveries, sending shares lower.",
     "CNBC"),
    (0, None, 1, 1.2, "Treasury yields ease after soft auction; risk assets rally",
     "A softer-than-expected 10-year auction pushed yields lower, giving a broad lift to equity markets into the close.",
     "Reuters"),
    (1, "AMD", 1, 5.2, "AMD lands multi-year hyperscaler deal for next-gen MI accelerators",
     "AMD announced a multi-year supply agreement with a leading hyperscaler for its upcoming MI-series AI accelerators, with analysts estimating over $6B in incremental revenue.",
     "Reuters"),
    (2, "NVDA", 1, 5.8, "NVIDIA tops Q3 estimates as data-center revenue jumps 42% YoY",
     "NVIDIA reported Q3 revenue of $71.2B, beating consensus. Data-center revenue rose 42% year over year, and guidance came in above expectations.",
     "Bloomberg"),
    (2, "COIN", -1, 7.4, "Bitcoin tumbles below $88K, crypto-linked stocks sell off",
     "Bitcoin fell below $88,000 amid heavy ETF outflows, dragging crypto-exposed equities sharply lower in afternoon trading.",
     "CoinDesk"),
    (3, None, 1, 1.6, "Fed holds rates steady, signals two cuts in 2027",
     "The Federal Reserve left rates unchanged and its dot plot signaled two cuts next year, sending major averages to session highs.",
     "CNBC"),
    (4, "MSFT", 1, 2.9, "Microsoft raises FY27 cloud guidance after Azure acceleration",
     "Microsoft raised its FY27 Azure growth outlook, citing accelerating AI workloads and improved enterprise commitment pipelines.",
     "WSJ"),
    (4, "AMZN", 1, 2.4, "AWS wins multi-year AI infrastructure contract with major bank",
     "Amazon Web Services secured a multi-year agreement to build AI infrastructure for one of the largest US banks, expanding its enterprise AI backlog.",
     "CNBC"),
    (5, "TSLA", -1, 6.1, "Tesla recalls 120K vehicles over Autopilot software issue",
     "Tesla is recalling roughly 120,000 vehicles after regulators flagged an Autopilot software defect; a fix will be delivered via over-the-air update.",
     "Reuters"),
    (6, "XOM", -1, 3.2, "Oil slides 4% as OPEC+ signals output increase",
     "Brent crude dropped 4% after OPEC+ signaled it would accelerate supply increases, pressuring integrated oil majors.",
     "Bloomberg"),
    (7, "NFLX", 1, 3.6, "Netflix hits 320M subscribers and announces price increase",
     "Netflix reported crossing 320 million paid subscribers and announced a broad price increase across its ad-free tiers.",
     "Variety"),
    (8, "AAPL", 1, 3.1, "Apple unveils M6 MacBooks with on-device AI assistant",
     "Apple introduced M6-powered MacBook Pro models featuring an upgraded neural engine and a fully on-device AI assistant.",
     "The Verge"),
    (9, "META", -1, 4.6, "Meta ad revenue growth slows while capex guidance is raised",
     "Meta reported slower ad revenue growth and raised 2027 capital expenditure guidance, unsettling investors focused on AI spending payoffs.",
     "WSJ"),
    (10, "GOOGL", 1, 2.6, "Alphabet's cloud backlog doubles on AI demand",
     "Alphabet said its Google Cloud backlog roughly doubled year over year, driven by demand for AI training and inference capacity.",
     "CNBC"),
    (11, "JPM", 1, 1.7, "JPMorgan lifts 2027 net interest income outlook",
     "JPMorgan raised its 2027 net interest income guidance, citing a resilient consumer and better-than-expected deposit margins.",
     "Bloomberg"),
    (13, None, -1, 1.4, "Core CPI hotter than expected at 3.1%, rate-cut hopes dim",
     "US core CPI rose 3.1% year over year, above forecasts, pressuring equities as traders trimmed expectations for near-term rate cuts.",
     "CNBC"),
    (18, "NVDA", 1, 3.4, "NVIDIA announces next-generation Rubin platform at GTC",
     "At GTC, NVIDIA previewed its Rubin platform, promising a step-change in AI training throughput with volume shipments expected late 2027.",
     "TechCrunch"),
    (21, "TSLA", 1, 4.2, "Tesla deliveries beat expectations on record China quarter",
     "Tesla delivered more vehicles than expected, helped by a record quarter in China and refreshed Model Y demand.",
     "Reuters"),
    (26, "META", 1, 2.8, "Meta launches standalone AI app with ad integration roadmap",
     "Meta launched a standalone AI assistant app and outlined plans to monetize through sponsored suggestions starting next year.",
     "The Verge"),
    (31, "XOM", 1, 2.1, "Exxon reports upstream beat as Guyana output hits record",
     "Exxon Mobil beat profit estimates on record production from its Guyana operations, offsetting weaker refining margins.",
     "Bloomberg"),
    (36, None, 0, 0.6, "US jobless claims steady; labor market stays resilient",
     "Weekly initial jobless claims were little changed, pointing to a labor market that continues to cool gradually without deteriorating.",
     "CNBC"),
]

DEMO_USER = ("demo", "demo123", "Demo User")
DEMO_WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "COIN"]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def trading_days(n: int, end: date) -> list:
    days = []
    d = end
    while len(days) < n:
        if d.weekday() < 5:  # Mon-Fri
            days.append(d)
        d -= timedelta(days=1)
    return list(reversed(days))


def gen_series(rng: random.Random, base: float, shocks: list) -> tuple:
    """Return (closes, volumes) for TRADING_DAYS days.

    shocks: list of (index, signed_magnitude_pct) — the news-driven moves.
    """
    rets = [rng.gauss(0, 0.013) for _ in range(TRADING_DAYS)]
    vols = [rng.uniform(0.8, 1.2) for _ in range(TRADING_DAYS)]
    for idx, signed_mag in shocks:
        if idx >= TRADING_DAYS:
            continue
        rets[idx] += signed_mag / 100.0
        if idx + 1 < TRADING_DAYS:          # momentum day after
            rets[idx + 1] += signed_mag / 100.0 * 0.35
        if idx + 2 < TRADING_DAYS:          # partial mean reversion
            rets[idx + 2] -= signed_mag / 100.0 * 0.25
        vols[idx] *= 2.5

    closes, c = [], base
    for r in rets:
        c *= (1.0 + r)
        closes.append(round(c, 2))
    volumes = [round(rng.uniform(18, 42) * 1e6 * v, 0) for v in vols]
    return closes, volumes


def run_seed(conn) -> None:
    cur = conn.cursor()

    for i, (ticker, name, sector, base) in enumerate(SYMBOLS, start=1):
        cur.execute("INSERT INTO symbols(id, ticker, name, sector) VALUES (?,?,?,?)",
                    (i, ticker, name, sector))
    conn.commit()

    cur.execute("INSERT INTO users(username, password_hash, display_name) VALUES (?,?,?)",
                (DEMO_USER[0], hash_password(DEMO_USER[1]), DEMO_USER[2]))
    conn.commit()

    dates = trading_days(TRADING_DAYS, LAST_DAY)
    news_rows = []
    # symbol -> list of (index, signed magnitude)
    per_symbol_shocks: dict = {t: [] for t, *_ in SYMBOLS}

    for n_id, (days_ago, ticker, sentiment, mag, headline, summary, source) in enumerate(NEWS, start=1):
        idx = TRADING_DAYS - 1 - days_ago
        signed = sentiment * mag
        if ticker is None:  # market-wide event touches every symbol
            for t, *_ in SYMBOLS:
                rng_scale = 0.5 + (stable_seed(f"{t}:{n_id}") % 50) / 100.0
                per_symbol_shocks[t].append((idx, signed * rng_scale))
            is_market = 1
        else:
            per_symbol_shocks[ticker].append((idx, signed))
            is_market = 0
        news_rows.append((headline, summary, source, dates[idx].isoformat(),
                          ticker, sentiment, mag, is_market))

    for i, (ticker, name, sector, base) in enumerate(SYMBOLS, start=1):
        rng = random.Random(stable_seed(ticker))
        closes, volumes = gen_series(rng, base, per_symbol_shocks[ticker])
        for d, c, v in zip(dates, closes, volumes):
            cur.execute(
                "INSERT INTO prices(symbol_id, date, close, volume) VALUES (?,?,?,?)",
                (i, d.isoformat(), c, v))
    conn.commit()

    for row in news_rows:
        cur.execute(
            "INSERT INTO news(headline, summary, source, published, ticker,"
            " sentiment, magnitude, is_market) VALUES (?,?,?,?,?,?,?,?)", row)
    conn.commit()

    demo_id = cur.execute("SELECT id FROM users WHERE username='demo'").fetchone()[0]
    for k, ticker in enumerate(DEMO_WATCHLIST):
        sid = cur.execute("SELECT id FROM symbols WHERE ticker=?", (ticker,)).fetchone()[0]
        cur.execute("INSERT INTO watchlist(user_id, symbol_id, added_at) VALUES (?,?,?)",
                    (demo_id, sid, (LAST_DAY - timedelta(days=30 - k)).isoformat()))
    conn.commit()
