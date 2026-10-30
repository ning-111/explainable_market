"""Explainable Market — a demo web app that links news events to price moves.

Run:  ../venv/bin/python app.py   (or ./run.sh)
Login with the built-in test account:  demo / demo123
"""
import sqlite3
from datetime import date, timedelta
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

import charts
import collector
import db

app = Flask(__name__)
app.secret_key = "explainable-market-demo-secret"

SENTIMENT_LABEL = {1: "Positive", 0: "Neutral", -1: "Negative"}


# ---------- helpers ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def price_rows(ticker):
    return db.q("""SELECT p.date, p.close, p.volume FROM prices p
                   JOIN symbols s ON s.id = p.symbol_id
                   WHERE s.ticker = ? ORDER BY p.date""", (ticker,))


def closes_by_date(ticker):
    return {r["date"]: r["close"] for r in price_rows(ticker)}


def move_around(ticker, day, window=3):
    """Return (day_move_pct, post_window_move_pct) around a news date, or None."""
    closes = closes_by_date(ticker)
    if day not in closes:
        return None
    dates = sorted(closes)
    i = dates.index(day)
    if i == 0:
        return None
    base = closes[dates[i - 1]]
    day_move = (closes[day] / base - 1) * 100
    post = closes[dates[min(i + window, len(dates) - 1)]] / base - 1
    post_move = post * 100
    return day_move, post_move


def news_for(ticker=None, sentiment=None, limit=200):
    sql = "SELECT * FROM news WHERE 1=1"
    params = []
    if ticker:
        sql += " AND (ticker = ? OR is_market = 1)"
        params.append(ticker)
    if sentiment in (1, 0, -1):
        sql += " AND sentiment = ?"
        params.append(sentiment)
    sql += " ORDER BY published DESC, id DESC LIMIT ?"
    params.append(limit)
    return db.q(sql, params)


def latest_n_dates(ticker, n=30):
    rows = price_rows(ticker)
    return rows[-n:]


def explain_move(ticker, day):
    """Find the most plausible news explanation for a move on `day`."""
    d = date.fromisoformat(day)
    candidates = db.q("""SELECT * FROM news
                         WHERE (ticker = ? OR is_market = 1)
                           AND published BETWEEN ? AND ?
                         ORDER BY ABS(magnitude) DESC""",
                      (ticker, (d - timedelta(days=1)).isoformat(), day))
    return candidates[0] if candidates else None


@app.template_filter("pct")
def pct(v):
    if v is None:
        return "—"
    return f"{v:+.2f}%"


@app.context_processor
def inject_globals():
    return {"sentiment_label": SENTIMENT_LABEL}


# ---------- auth ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    prefill_user = prefill_pass = ""
    if request.args.get("demo"):
        prefill_user, prefill_pass = "demo", "demo123"
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.q1("SELECT * FROM users WHERE username = ?", (username,))
        if user and user["password_hash"] == hash_password(password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['display_name']}!", "success")
            return redirect(request.args.get("next") or url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error,
                           prefill_user=prefill_user, prefill_pass=prefill_pass)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


# ---------- pages ----------

@app.route("/")
@login_required
def dashboard():
    uid = session["user_id"]
    watch = db.q("""SELECT s.ticker, s.name, s.sector FROM watchlist w
                    JOIN symbols s ON s.id = w.symbol_id
                    WHERE w.user_id = ? ORDER BY w.added_at""", (uid,))

    watch_cards = []
    for row in watch:
        rows = price_rows(row["ticker"])
        last, prev = rows[-1], rows[-2]
        change = (last["close"] / prev["close"] - 1) * 100
        watch_cards.append({
            "ticker": row["ticker"], "name": row["name"], "sector": row["sector"],
            "close": last["close"], "change": change,
            "sparkline": charts.sparkline([r["close"] for r in rows[-30:]]),
        })

    movers = []
    for card in watch_cards:
        day = db.q1("""SELECT p.date FROM prices p JOIN symbols s ON s.id=p.symbol_id
                       WHERE s.ticker=? ORDER BY p.date DESC LIMIT 1""", (card["ticker"],))
        news = explain_move(card["ticker"], day["date"])
        movers.append({**card, "date": day["date"], "news": news,
                       "abs_move": abs(card["change"])})
    movers.sort(key=lambda m: m["abs_move"], reverse=True)
    movers = movers[:4]

    recent_news = news_for(limit=8)
    return render_template("dashboard.html", watch=watch_cards, movers=movers,
                           recent_news=recent_news)


@app.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    uid = session["user_id"]
    if request.method == "POST":
        action = request.form.get("action")
        ticker = request.form.get("ticker", "").strip().upper()
        sym = db.q1("SELECT * FROM symbols WHERE ticker = ?", (ticker,))
        if not sym:
            flash(f"Unknown symbol: {ticker}", "error")
        elif action == "add":
            try:
                db.x("INSERT INTO watchlist(user_id, symbol_id, added_at) VALUES (?,?,?)",
                     (uid, sym["id"], date.today().isoformat()))
                flash(f"{ticker} added to your watchlist.", "success")
            except sqlite3.IntegrityError:
                flash(f"{ticker} is already on your watchlist.", "info")
        elif action == "remove":
            db.x("DELETE FROM watchlist WHERE user_id = ? AND symbol_id = ?",
                 (uid, sym["id"]))
            flash(f"{ticker} removed from your watchlist.", "info")
        return redirect(url_for("watchlist"))

    watch = db.q("""SELECT s.ticker, s.name, s.sector FROM watchlist w
                    JOIN symbols s ON s.id = w.symbol_id
                    WHERE w.user_id = ? ORDER BY w.added_at""", (uid,))
    watch_tickers = {r["ticker"] for r in watch}
    all_symbols = db.q("SELECT * FROM symbols ORDER BY ticker")
    return render_template("watchlist.html", watch=watch, all_symbols=all_symbols,
                           watch_tickers=watch_tickers)


@app.route("/symbol/<ticker>")
@login_required
def symbol_detail(ticker):
    ticker = ticker.upper()
    sym = db.q1("SELECT * FROM symbols WHERE ticker = ?", (ticker,))
    if not sym:
        flash(f"Unknown symbol: {ticker}", "error")
        return redirect(url_for("dashboard"))

    rows = price_rows(ticker)
    dates = [r["date"] for r in rows]
    closes = [r["close"] for r in rows]
    last, prev = closes[-1], closes[-2]
    change = (last / prev - 1) * 100
    period_change = (closes[-1] / closes[0] - 1) * 100

    news_items = news_for(ticker=ticker)
    news_by_date = {}
    for n in news_items:
        news_by_date.setdefault(n["published"], []).append(n)
    markers = []
    for i, d in enumerate(dates):
        for n in news_by_date.get(d, []):
            markers.append((i, n["sentiment"], n["headline"], bool(n["is_market"])))

    uid = session["user_id"]
    on_watchlist = bool(db.q1(
        """SELECT 1 FROM watchlist w JOIN symbols s ON s.id=w.symbol_id
           WHERE w.user_id=? AND s.ticker=?""", (uid, ticker)))

    impacts = []
    for n in news_items:
        mv = move_around(ticker, n["published"])
        impacts.append({"news": n, "day_move": mv[0] if mv else None,
                        "post_move": mv[1] if mv else None,
                        "consistent": (mv is not None and n["sentiment"] != 0
                                       and (mv[0] > 0) == (n["sentiment"] > 0))})
    impacts.reverse()  # oldest first for the timeline table

    return render_template("symbol.html", sym=sym, close=last, change=change,
                           period_change=period_change, high=max(closes), low=min(closes),
                           chart=charts.price_chart(dates, closes, markers),
                           impacts=impacts, on_watchlist=on_watchlist,
                           news_count=len(news_items))


@app.route("/news")
@login_required
def news_page():
    ticker = request.args.get("ticker", "").strip().upper() or None
    sentiment = request.args.get("sentiment", type=int)
    items = []
    for n in news_for(ticker=ticker, sentiment=sentiment):
        impact = None
        if n["ticker"]:
            mv = move_around(n["ticker"], n["published"])
            if mv:
                impact = mv[0]
        items.append({"n": n, "impact": impact})
    symbols = db.q("SELECT ticker, name FROM symbols ORDER BY ticker")
    return render_template("news.html", items=items, symbols=symbols,
                           sel_ticker=ticker, sel_sentiment=sentiment)


@app.route("/news/collect", methods=["POST"])
@login_required
def news_collect():
    try:
        count = collector.collect()
    except Exception as exc:  # demo app: never crash on the collector
        flash(f"News collection failed: {exc}", "error")
        return redirect(url_for("news_page"))
    if count:
        flash(f"News collection finished: {count} new sample item(s) added.", "success")
    else:
        flash("News collection finished: nothing new to add.", "info")
    return redirect(url_for("news_page"))


if __name__ == "__main__":
    db.init()
    app.run(host="127.0.0.1", port=5050, debug=False)
