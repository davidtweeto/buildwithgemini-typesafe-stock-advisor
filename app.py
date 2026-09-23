import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from stock_recommender import evaluate_ticker, StockRecommendation
from feed_data import FEED_ITEMS
from live_feed import get_live_dossier, fetch_24h_news, fetch_24h_tweets
from typesafe_sdk import TypeSafeClient

load_dotenv()

app = FastAPI(title="TypeSafe Stock Recommendations", version="1.0.0")

# In-memory cache for latest recommendations
CACHE_FILE = "/config/dev/jev/recommendations_latest.json" if os.path.exists("/config/dev/jev/recommendations_latest.json") else "recommendations_latest.json"

class EvaluateRequest(BaseModel):
    ticker: str
    company: str
    sector: str = "General"
    news: List[str]
    tweets: List[str]

class AutoEvaluateRequest(BaseModel):
    ticker: str
    company: str = ""
    sector: str = "General"


def get_cached_recommendations():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok", "model": "typesafe/jev-1.13", "api_key_set": bool(os.getenv("TYPESAFE_API_KEY"))}


@app.get("/api/recommendations")
def api_recommendations():
    data = get_cached_recommendations()
    return JSONResponse(content={"items": data, "count": len(data)})


@app.post("/api/evaluate")
def api_evaluate(req: EvaluateRequest):
    if not os.getenv("TYPESAFE_API_KEY"):
        raise HTTPException(status_code=500, detail="TYPESAFE_API_KEY is not configured on the server")
    
    if not req.news and not req.tweets:
        raise HTTPException(status_code=400, detail="Please provide at least one news item or tweet.")

    client = TypeSafeClient()
    item = {
        "ticker": req.ticker.upper().strip(),
        "company": req.company.strip(),
        "sector": req.sector.strip(),
        "last_24h_news": req.news,
        "last_24h_tweets": req.tweets
    }
    try:
        rec = evaluate_ticker(client, item)
        rec_dict = {
            "ticker": rec.ticker,
            "company": rec.company,
            "sector": rec.sector,
            "recommendation": rec.recommendation,
            "composite_score": rec.composite_score,
            "confidence": rec.confidence,
            "directional_bias": rec.directional_bias,
            "bias_probabilities": rec.bias_probabilities,
            "materiality_score": rec.materiality_score,
            "actionable_catalyst_prob": rec.actionable_catalyst_prob,
            "risk_factor_prob": rec.risk_factor_prob,
            "hype_profile": rec.hype_profile,
            "key_catalysts": rec.key_catalysts,
            "risks_and_headwinds": rec.risks_and_headwinds,
            "rationale": rec.rationale
        }
        return JSONResponse(content=rec_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fetch-feed/{ticker}")
def api_fetch_feed(ticker: str):
    news = fetch_24h_news(ticker, limit=4)
    tweets = fetch_24h_tweets(ticker, limit=4)
    return JSONResponse(content={
        "ticker": ticker.upper().strip(),
        "news": news,
        "tweets": tweets
    })


@app.post("/api/auto-evaluate")
def api_auto_evaluate(req: AutoEvaluateRequest):
    if not os.getenv("TYPESAFE_API_KEY"):
        raise HTTPException(status_code=500, detail="TYPESAFE_API_KEY is not configured on the server")

    ticker_clean = req.ticker.upper().strip()
    if not ticker_clean:
        raise HTTPException(status_code=400, detail="Ticker cannot be empty")

    dossier = get_live_dossier(ticker_clean, company=req.company, sector=req.sector)
    client = TypeSafeClient()

    try:
        rec = evaluate_ticker(client, dossier)
        rec_dict = {
            "ticker": rec.ticker,
            "company": rec.company,
            "sector": rec.sector,
            "recommendation": rec.recommendation,
            "composite_score": rec.composite_score,
            "confidence": rec.confidence,
            "directional_bias": rec.directional_bias,
            "bias_probabilities": rec.bias_probabilities,
            "materiality_score": rec.materiality_score,
            "actionable_catalyst_prob": rec.actionable_catalyst_prob,
            "risk_factor_prob": rec.risk_factor_prob,
            "hype_profile": rec.hype_profile,
            "key_catalysts": rec.key_catalysts,
            "risks_and_headwinds": rec.risks_and_headwinds,
            "rationale": rec.rationale,
            "fetched_news": dossier["last_24h_news"],
            "fetched_tweets": dossier["last_24h_tweets"]
        }

        # Update cache file if writable
        try:
            cached = get_cached_recommendations()
            # Replace existing or prepend
            updated = [x for x in cached if x.get("ticker") != rec.ticker]
            updated.insert(0, rec_dict)
            with open(CACHE_FILE, "w") as f:
                json.dump(updated, f, indent=2)
        except Exception:
            pass

        return JSONResponse(content=rec_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index():
    recs = get_cached_recommendations()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    cards_html = ""
    for r in recs:
        rec = r.get("recommendation", "HOLD")
        badge_class = "badge-neutral"
        if "STRONG BUY" in rec:
            badge_class = "badge-strong-buy"
        elif "BUY" in rec:
            badge_class = "badge-buy"
        elif "SELL" in rec:
            badge_class = "badge-sell"
        elif "REDUCE" in rec or "UNDERWEIGHT" in rec:
            badge_class = "badge-reduce"

        probs = r.get("bias_probabilities", {})
        prob_bars = "".join(
            f'<div class="prob-row"><span>{k.replace("_", " ").title()}</span>'
            f'<div class="bar-container"><div class="bar" style="width: {v*100:.1f}%;"></div>'
            f'<span>{v*100:.1f}%</span></div></div>'
            for k, v in probs.items() if v > 0.01
        )

        catalysts = "".join(f"<li>{c}</li>" for c in r.get("key_catalysts", []))
        risks = "".join(f"<li>{rk}</li>" for rk in r.get("risks_and_headwinds", []))

        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <div class="card-header-left">
                    <span class="ticker">{r['ticker']}</span>
                    <span class="company">{r['company']}</span>
                    <span class="sector">{r.get('sector', '')}</span>
                </div>
                <div class="badge {badge_class}">{rec}</div>
            </div>
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-title">Composite Score</div>
                    <div class="metric-val">{r['composite_score']:+.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Jev Confidence</div>
                    <div class="metric-val">{r['confidence']*100:.0f}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Materiality</div>
                    <div class="metric-val">{r['materiality_score']:.1f} / 3.0</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Actionable Prob</div>
                    <div class="metric-val">{r['actionable_catalyst_prob']*100:.0f}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Risk Overhang</div>
                    <div class="metric-val">{r['risk_factor_prob']*100:.0f}%</div>
                </div>
            </div>

            <div class="details-section">
                <h4>Jev Directional Probabilities</h4>
                <div class="prob-list">
                    {prob_bars}
                </div>
            </div>

            <div class="details-section">
                <h4>Rationale & Synthesis</h4>
                <p class="rationale-text">{r.get('rationale', '')}</p>
            </div>

            <div class="columns-two">
                <div>
                    <h4>Key 24h Catalysts</h4>
                    <ul class="catalyst-list">{catalysts}</ul>
                </div>
                <div>
                    <h4>Headwinds & Risks</h4>
                    <ul class="risk-list">{risks}</ul>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <meta name="theme-color" content="#0b0f19">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>TypeSafe Stock Exchange Recommendations (Jev-1.13)</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --card-bg: #141c2e;
            --card-border: #24324d;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.25);
            --green: #22c55e;
            --yellow: #eab308;
            --red: #ef4444;
            --orange: #f97316;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 30px 20px;
        }}
        .header {{
            max-width: 1100px;
            margin: 0 auto 30px auto;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 24px;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .live-tag {{
            background: #0284c7;
            color: #fff;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 14px;
            margin: 8px 0 0 0;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 28px;
        }}
        
        /* Interactive Live Form */
        .eval-panel {{
            background: linear-gradient(145deg, #162035, #111a2c);
            border: 1px solid #2d3e60;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }}
        .eval-panel h2 {{
            margin: 0 0 8px 0;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .panel-desc {{
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 18px;
        }}
        .form-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 14px;
            margin-bottom: 14px;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .form-group label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
        }}
        input, textarea {{
            background: #0b111d;
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}
        input:focus, textarea:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 2px var(--accent-glow);
        }}
        .textarea-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-bottom: 16px;
        }}
        textarea {{
            resize: vertical;
            min-height: 85px;
            font-family: inherit;
        }}
        .btn-submit {{
            color: white;
            border: none;
            padding: 12px 22px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
        }}
        .btn-submit:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
        }}
        .button-group {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 8px;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
        }}
        .btn-primary:hover:not(:disabled) {{
            background: linear-gradient(135deg, #0369a1, #1d4ed8);
            transform: translateY(-1px);
        }}
        .btn-secondary {{
            background: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8;
        }}
        .btn-secondary:hover:not(:disabled) {{
            background: #24344d;
            color: #f1f5f9;
        }}
        .btn-tertiary {{
            background: #334155;
            color: #e2e8f0;
        }}
        .btn-tertiary:hover:not(:disabled) {{
            background: #475569;
        }}

        /* Cards */
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .card-header-left {{
            display: flex;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .ticker {{
            font-size: 24px;
            font-weight: 700;
            color: var(--text-main);
            margin-right: 12px;
        }}
        .company {{
            font-size: 18px;
            color: var(--text-muted);
            margin-right: 12px;
        }}
        .sector {{
            font-size: 12px;
            background: #0b111d;
            padding: 4px 10px;
            border-radius: 20px;
            color: var(--accent);
            border: 1px solid var(--card-border);
        }}
        .badge {{
            font-size: 13px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 8px;
            letter-spacing: 0.5px;
        }}
        .badge-strong-buy {{ background: rgba(34, 197, 94, 0.18); color: #4ade80; border: 1px solid #22c55e; }}
        .badge-buy {{ background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid #38bdf8; }}
        .badge-neutral {{ background: rgba(234, 179, 8, 0.18); color: #facc15; border: 1px solid #eab308; }}
        .badge-reduce {{ background: rgba(249, 115, 22, 0.18); color: #fb923c; border: 1px solid #f97316; }}
        .badge-sell {{ background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid #ef4444; }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        .metric-box {{
            background: #0b111d;
            border: 1px solid var(--card-border);
            padding: 12px 14px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-title {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 6px;
        }}
        .metric-val {{
            font-size: 20px;
            font-weight: 700;
        }}
        .details-section {{
            margin-top: 16px;
        }}
        .details-section h4, .columns-two h4 {{
            margin: 0 0 8px 0;
            font-size: 13px;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
        .prob-list {{
            background: #0b111d;
            padding: 12px 16px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border: 1px solid var(--card-border);
        }}
        .prob-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }}
        .bar-container {{
            display: flex;
            align-items: center;
            gap: 10px;
            width: 60%;
        }}
        .bar {{
            height: 8px;
            background: var(--accent);
            border-radius: 4px;
        }}
        .columns-two {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
            font-size: 13px;
            line-height: 1.6;
            color: #cbd5e1;
        }}
        .rationale-text {{
            font-size: 13px;
            line-height: 1.5;
            color: #e2e8f0;
            background: #0b111d;
            padding: 12px 16px;
            border-left: 3px solid var(--accent);
            border-radius: 4px;
            margin: 0;
            border-top: 1px solid var(--card-border);
            border-right: 1px solid var(--card-border);
            border-bottom: 1px solid var(--card-border);
        }}
        #live-result-container {{
            margin-top: 20px;
            display: none;
        }}

        /* Responsive Breakpoints for Tablet & Mobile */
        @media (max-width: 820px) {{
            body {{
                padding: 18px 14px;
            }}
            .header {{
                margin-bottom: 20px;
                padding-bottom: 18px;
            }}
            .header h1 {{
                font-size: 21px;
                flex-wrap: wrap;
            }}
            .subtitle {{
                font-size: 13px;
            }}
            .eval-panel {{
                padding: 18px 16px;
            }}
            .form-grid {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            .textarea-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            .columns-two {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
            .metric-box:last-child {{
                grid-column: span 2;
            }}
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 12px 10px;
            }}
            .container {{
                gap: 20px;
            }}
            .header h1 {{
                font-size: 19px;
            }}
            .header-top {{
                gap: 10px;
            }}
            .eval-panel {{
                padding: 14px 12px;
                border-radius: 10px;
            }}
            .eval-panel h2 {{
                font-size: 16px;
                line-height: 1.3;
            }}
            .panel-desc {{
                font-size: 12px;
                margin-bottom: 14px;
            }}
            input, textarea {{
                font-size: 16px; /* Prevents auto-zoom on iOS Safari */
                padding: 10px;
            }}
            textarea {{
                min-height: 75px;
            }}
            .button-group {{
                flex-direction: column;
                gap: 8px;
                width: 100%;
            }}
            .btn-submit {{
                width: 100%;
                justify-content: center;
                min-height: 48px; /* Touch target accessibility */
                font-size: 14px;
                padding: 12px 16px;
            }}
            .card {{
                padding: 16px 14px;
                border-radius: 10px;
            }}
            .card-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
                margin-bottom: 16px;
            }}
            .card-header-left {{
                width: 100%;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 6px;
            }}
            .ticker {{
                font-size: 22px;
                margin-right: 4px;
            }}
            .company {{
                font-size: 15px;
                margin-right: 4px;
            }}
            .sector {{
                font-size: 11px;
                padding: 2px 8px;
            }}
            .badge {{
                font-size: 12px;
                padding: 5px 12px;
                align-self: flex-start;
            }}
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
                margin-bottom: 16px;
            }}
            .metric-box {{
                padding: 10px 8px;
            }}
            .metric-title {{
                font-size: 10px;
            }}
            .metric-val {{
                font-size: 17px;
            }}
            .prob-row {{
                font-size: 12px;
            }}
            .bar-container {{
                width: 52%;
                gap: 6px;
            }}
            .bar-container span {{
                font-size: 11px;
                min-width: 34px;
                text-align: right;
            }}
            .rationale-text {{
                font-size: 12px;
                padding: 10px 12px;
            }}
            ul {{
                padding-left: 18px;
                font-size: 12px;
            }}
        }}

        @media (max-width: 360px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .metric-box:last-child {{
                grid-column: span 1;
            }}
            .bar-container {{
                width: 45%;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-top">
            <div>
                <h1>📊 TypeSafe Stock Exchange Intelligence <span class="live-tag">System One</span></h1>
                <p class="subtitle">Evaluated via TypeSafe AI Jev-1.13 decision model & composite scoring. Last updated: {timestamp}</p>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Interactive Analysis Tool -->
        <div class="eval-panel">
            <h2>⚡ Run Live Jev Evaluation on Any Stock</h2>
            <p class="panel-desc">Submit 24h headlines and tweets for any ticker. Jev System One evaluates market bias, materiality, actionable catalysts, and risk factors in parallel.</p>
            
            <form id="evalForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Ticker Symbol</label>
                        <input type="text" id="ticker" placeholder="e.g. AAPL" required>
                    </div>
                    <div class="form-group">
                        <label>Company Name</label>
                        <input type="text" id="company" placeholder="e.g. Apple Inc." required>
                    </div>
                    <div class="form-group">
                        <label>Sector</label>
                        <input type="text" id="sector" placeholder="e.g. Consumer Electronics">
                    </div>
                </div>

                <div class="textarea-grid">
                    <div class="form-group">
                        <label>24h News Headlines (one per line)</label>
                        <textarea id="news" placeholder="Paste news wires or earnings announcements..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label>24h Social / Tweets (one per line)</label>
                        <textarea id="tweets" placeholder="Paste investor tweets or social discussions..." required></textarea>
                    </div>
                </div>

                <div class="button-group">
                    <button type="button" class="btn-submit btn-primary" id="autoFetchBtn">
                        <span>⚡ Auto-Fetch 24h Feed & Evaluate</span>
                    </button>
                    <button type="button" class="btn-submit btn-secondary" id="previewFeedBtn">
                        <span>📥 Fetch 24h News & Tweets into Form</span>
                    </button>
                    <button type="submit" class="btn-submit btn-tertiary" id="submitBtn">
                        <span>Evaluate Form Text</span>
                    </button>
                </div>
            </form>

            <div id="live-result-container"></div>
        </div>

        <!-- 24h Default Recommendations -->
        <h2>Market 24-Hour Dossiers (Evaluated by Jev)</h2>
        <div id="cards-container">
            {cards_html}
        </div>
    </div>

    <script>
        const form = document.getElementById('evalForm');
        const submitBtn = document.getElementById('submitBtn');
        const autoFetchBtn = document.getElementById('autoFetchBtn');
        const previewFeedBtn = document.getElementById('previewFeedBtn');
        const resultContainer = document.getElementById('live-result-container');

        // Helper to render card
        function renderCard(data) {{
            let badgeClass = 'badge-neutral';
            if (data.recommendation.includes('STRONG BUY')) badgeClass = 'badge-strong-buy';
            else if (data.recommendation.includes('BUY')) badgeClass = 'badge-buy';
            else if (data.recommendation.includes('SELL')) badgeClass = 'badge-sell';
            else if (data.recommendation.includes('REDUCE') || data.recommendation.includes('UNDERWEIGHT')) badgeClass = 'badge-reduce';

            let probBars = '';
            for (const [k, v] of Object.entries(data.bias_probabilities || {{}})) {{
                if (v > 0.01) {{
                    probBars += `
                    <div class="prob-row">
                        <span>${{k.replace(/_/g, ' ')}}</span>
                        <div class="bar-container">
                            <div class="bar" style="width: ${{v * 100}}%;"></div>
                            <span>${{(v * 100).toFixed(1)}}%</span>
                        </div>
                    </div>`;
                }}
            }}

            let newsList = (data.fetched_news || data.key_catalysts || []).map(n => `<li>${{n}}</li>`).join('');
            let tweetList = (data.fetched_tweets || data.risks_and_headwinds || []).map(t => `<li>${{t}}</li>`).join('');

            resultContainer.innerHTML = `
            <div class="card" style="border-color: var(--accent); margin-top: 16px;">
                <div class="card-header">
                    <div class="card-header-left">
                        <span class="ticker">${{data.ticker}}</span>
                        <span class="company">${{data.company}}</span>
                        <span class="sector">${{data.sector}}</span>
                    </div>
                    <div class="badge ${{badgeClass}}">${{data.recommendation}}</div>
                </div>
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-title">Composite Score</div>
                        <div class="metric-val">${{data.composite_score > 0 ? '+' : ''}}${{data.composite_score.toFixed(2)}}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-title">Jev Confidence</div>
                        <div class="metric-val">${{(data.confidence * 100).toFixed(0)}}%</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-title">Materiality</div>
                        <div class="metric-val">${{data.materiality_score.toFixed(1)}} / 3.0</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-title">Actionable Prob</div>
                        <div class="metric-val">${{(data.actionable_catalyst_prob * 100).toFixed(0)}}%</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-title">Risk Overhang</div>
                        <div class="metric-val">${{(data.risk_factor_prob * 100).toFixed(0)}}%</div>
                    </div>
                </div>
                <div class="details-section">
                    <h4>Jev Directional Probabilities</h4>
                    <div class="prob-list">${{probBars}}</div>
                </div>
                <div class="details-section">
                    <h4>Synthesized Rationale</h4>
                    <p class="rationale-text">${{data.rationale}}</p>
                </div>
                <div class="columns-two">
                    <div>
                        <h4>24h News Ingested</h4>
                        <ul>${{newsList}}</ul>
                    </div>
                    <div>
                        <h4>24h Social & Tweets Ingested</h4>
                        <ul>${{tweetList}}</ul>
                    </div>
                </div>
            </div>`;
        }}

        // 1. Auto-Fetch and Evaluate with Jev
        autoFetchBtn.addEventListener('click', async () => {{
            const ticker = document.getElementById('ticker').value.trim();
            if (!ticker) {{
                alert("Please enter a ticker symbol first (e.g. AAPL, NVDA, GOOGL, MSFT)");
                return;
            }}

            autoFetchBtn.disabled = true;
            autoFetchBtn.innerText = "⏳ Fetching 24h Feed & Analyzing with Jev...";
            resultContainer.style.display = 'block';
            resultContainer.innerHTML = '<div style="padding: 16px; color: var(--accent);">📡 Fetching 24h news and tweets, then invoking TypeSafe Jev System One...</div>';

            try {{
                const res = await fetch('/api/auto-evaluate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        ticker: ticker,
                        company: document.getElementById('company').value.trim(),
                        sector: document.getElementById('sector').value.trim() || 'General'
                    }})
                }});
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Evaluation failed');

                // Populate textareas with what was fetched
                if (data.fetched_news) document.getElementById('news').value = data.fetched_news.join('\\n');
                if (data.fetched_tweets) document.getElementById('tweets').value = data.fetched_tweets.join('\\n');
                if (data.company) document.getElementById('company').value = data.company;

                renderCard(data);
            }} catch (err) {{
                resultContainer.innerHTML = `<div style="color: var(--red); padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">Error: ${{err.message}}</div>`;
            }} finally {{
                autoFetchBtn.disabled = false;
                autoFetchBtn.innerText = "⚡ Auto-Fetch 24h Feed & Evaluate";
            }}
        }});

        // 2. Fetch Feed into Form Only
        previewFeedBtn.addEventListener('click', async () => {{
            const ticker = document.getElementById('ticker').value.trim();
            if (!ticker) {{
                alert("Please enter a ticker symbol first (e.g. AAPL)");
                return;
            }}
            previewFeedBtn.disabled = true;
            previewFeedBtn.innerText = "Fetching...";
            try {{
                const res = await fetch(`/api/fetch-feed/${{encodeURIComponent(ticker)}}`);
                const data = await res.json();
                document.getElementById('news').value = (data.news || []).join('\\n');
                document.getElementById('tweets').value = (data.tweets || []).join('\\n');
            }} catch (err) {{
                alert("Failed to fetch feed: " + err.message);
            }} finally {{
                previewFeedBtn.disabled = false;
                previewFeedBtn.innerText = "📥 Fetch 24h News & Tweets into Form";
            }}
        }});

        // 3. Manual Form Submit
        form.addEventListener('submit', async (e) => {{
            e.preventDefault();
            submitBtn.disabled = true;
            submitBtn.innerText = "Analyzing...";
            resultContainer.style.display = 'block';
            resultContainer.innerHTML = '<div style="padding: 16px; color: var(--accent);">Calling TypeSafe System One API (Jev-1.13)...</div>';

            const payload = {{
                ticker: document.getElementById('ticker').value,
                company: document.getElementById('company').value || document.getElementById('ticker').value + ' Inc.',
                sector: document.getElementById('sector').value || 'General',
                news: document.getElementById('news').value.split('\\n').filter(s => s.trim().length > 0),
                tweets: document.getElementById('tweets').value.split('\\n').filter(s => s.trim().length > 0)
            }};

            try {{
                const res = await fetch('/api/evaluate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Evaluation failed');

                renderCard(data);
            }} catch (err) {{
                resultContainer.innerHTML = `<div style="color: var(--red); padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">Error: ${{err.message}}</div>`;
            }} finally {{
                submitBtn.disabled = false;
                submitBtn.innerText = "Evaluate Form Text";
            }}
        }});
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
