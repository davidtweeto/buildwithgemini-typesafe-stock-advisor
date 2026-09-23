#!/usr/bin/env python3
"""
Generates an interactive, styled HTML dashboard from recommendations_latest.json
"""

import json
from datetime import datetime

def generate_html_report():
    with open("/config/dev/jev/recommendations_latest.json") as f:
        data = json.load(f)

    from datetime import timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    card_html = ""
    for r in data:
        rec = r["recommendation"]
        badge_class = "badge-neutral"
        if "STRONG BUY" in rec:
            badge_class = "badge-strong-buy"
        elif "BUY" in rec:
            badge_class = "badge-buy"
        elif "SELL" in rec:
            badge_class = "badge-sell"
        elif "REDUCE" in rec or "UNDERWEIGHT" in rec:
            badge_class = "badge-reduce"

        probs = r["bias_probabilities"]
        prob_bars = "".join(
            f'<div class="prob-row"><span>{k.replace("_", " ").title()}</span>'
            f'<div class="bar-container"><div class="bar" style="width: {v*100:.1f}%;"></div>'
            f'<span>{v*100:.1f}%</span></div></div>'
            for k, v in probs.items() if v > 0.01
        )

        catalysts_html = "".join(f"<li>{c}</li>" for c in r["key_catalysts"])
        risks_html = "".join(f"<li>{rk}</li>" for rk in r["risks_and_headwinds"])

        card_html += f"""
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="ticker">{r['ticker']}</span>
                    <span class="company">{r['company']}</span>
                    <span class="sector">{r['sector']}</span>
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
                <p class="rationale-text">{r['rationale']}</p>
            </div>

            <div class="columns-two">
                <div>
                    <h4>Key 24h Catalysts</h4>
                    <ul class="catalyst-list">{catalysts_html}</ul>
                </div>
                <div>
                    <h4>Headwinds & Risks</h4>
                    <ul class="risk-list">{risks_html}</ul>
                </div>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TypeSafe AI Stock Recommendations (Jev-1.13)</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --green: #22c55e;
            --yellow: #eab308;
            --red: #ef4444;
            --orange: #f97316;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 30px;
        }}
        .header {{
            max-width: 1100px;
            margin: 0 auto 30px auto;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 15px;
            margin: 0;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
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
            font-size: 13px;
            background: #0f172a;
            padding: 4px 10px;
            border-radius: 20px;
            color: var(--accent);
            border: 1px solid #334155;
        }}
        .badge {{
            font-size: 14px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 8px;
            letter-spacing: 0.5px;
        }}
        .badge-strong-buy {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }}
        .badge-buy {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }}
        .badge-neutral {{ background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }}
        .badge-reduce {{ background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid #f97316; }}
        .badge-sell {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        .metric-box {{
            background: #0f172a;
            border: 1px solid #334155;
            padding: 12px 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-title {{
            font-size: 12px;
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
            font-size: 14px;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
        .prob-list {{
            background: #0f172a;
            padding: 12px 16px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
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
            font-size: 14px;
            line-height: 1.6;
            color: #cbd5e1;
        }}
        .rationale-text {{
            font-size: 14px;
            line-height: 1.5;
            color: #e2e8f0;
            background: #111827;
            padding: 12px 16px;
            border-left: 3px solid var(--accent);
            border-radius: 4px;
            margin: 0;
        }}

        /* Responsive Breakpoints for Mobile & Tablet */
        @media (max-width: 768px) {{
            body {{
                padding: 14px 10px;
            }}
            .header {{
                margin-bottom: 20px;
                padding-bottom: 16px;
            }}
            .header h1 {{
                font-size: 20px;
                flex-wrap: wrap;
            }}
            .subtitle {{
                font-size: 13px;
            }}
            .card {{
                padding: 16px 14px;
            }}
            .card-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
                margin-bottom: 16px;
            }}
            .card-header > div:first-child {{
                display: flex;
                flex-wrap: wrap;
                align-items: baseline;
                gap: 6px;
            }}
            .badge {{
                align-self: flex-start;
            }}
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            .metric-box:last-child {{
                grid-column: span 2;
            }}
            .metric-val {{
                font-size: 17px;
            }}
            .columns-two {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .bar-container {{
                width: 50%;
            }}
        }}

        @media (max-width: 480px) {{
            .prob-row {{
                font-size: 12px;
            }}
            .bar-container {{
                width: 45%;
                gap: 6px;
            }}
            .badge {{
                font-size: 11px;
                padding: 4px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 TypeSafe AI Stock Exchange Recommendations</h1>
        <p class="subtitle">Powered by System One (Jev-1.13) Decision Primitives & Composite Scoring | Generated at {timestamp}</p>
    </div>
    <div class="container">
        {card_html}
    </div>
</body>
</html>
"""

    report_path = "/config/dev/jev/report.html"
    with open(report_path, "w") as f:
        f.write(html_content)
    print(f"[✓] Dashboard generated at {report_path}")

if __name__ == "__main__":
    generate_html_report()
