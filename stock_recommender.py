#!/usr/bin/env python3
"""
Stock Exchange Recommendations Engine
Powered by TypeSafe AI (System One Jev Model) & Composite Scoring
Evaluates 24-Hour Financial News and Social Media (Twitter/X) Chatter
"""

import os
import sys
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul

# Load environment
load_dotenv()
API_KEY = os.getenv("TYPESAFE_API_KEY")

if not API_KEY:
    print("Error: TYPESAFE_API_KEY environment variable not set in .env", file=sys.stderr)
    sys.exit(1)


@dataclass
class StockRecommendation:
    ticker: str
    company: str
    sector: str
    recommendation: str
    composite_score: float
    confidence: float
    directional_bias: str
    bias_probabilities: Dict[str, float]
    materiality_score: float
    actionable_catalyst_prob: float
    risk_factor_prob: float
    hype_profile: str
    key_catalysts: List[str]
    risks_and_headwinds: List[str]
    rationale: str


def evaluate_ticker(client: TypeSafeClient, item: Dict[str, Any]) -> StockRecommendation:
    ticker = item["ticker"]
    company = item["company"]
    sector = item["sector"]
    news = item["last_24h_news"]
    tweets = item["last_24h_tweets"]

    state = {
        "ticker": ticker,
        "company": company,
        "sector": sector,
        "news_events_last_24h": news,
        "social_tweets_last_24h": tweets
    }

    # Parallel System One Questions to Jev
    questions = {
        "market_bias": Choice(
            instructions=(
                "Based on the last 24h news and tweets, evaluate the net directional sentiment "
                "and catalyst momentum for this stock."
            ),
            criteria={
                "strong_bullish": "High-conviction positive catalysts: blowout earnings beat, huge revenue guidance increase, major breakout, heavy institutional backing",
                "moderate_bullish": "Constructive positive momentum: favorable product launch, rating upgrade, or positive industry tailwinds outweighing minor concerns",
                "neutral_or_mixed": "Balanced or conflicting signals: market rotation, hold stance, lack of clear catalyst, or wait-and-see posture",
                "moderate_bearish": "Negative headwinds: delivery revisions, margin compression, valuation concerns, or regulatory scrutiny causing short-term drag",
                "strong_bearish": "Severe negative catalysts: major earnings miss, accounting scandal, formal enforcement lawsuit, or existential business model threat"
            }
        ),
        "materiality": Score(
            instructions="Rate the financial and valuation materiality of the 24h catalysts on a 4-level scale.",
            criteria=[
                "Level 0: Minor social media noise or routine commentary with negligible impact on corporate valuation",
                "Level 1: Modest intraday developments or routine executive commentary causing small price fluctuations",
                "Level 2: Meaningful catalysts such as product launches, price target hikes, or margin shifts that affect quarterly results",
                "Level 3: Transformative, high-impact catalysts such as blowout earnings revisions, mega acquisitions, or major regulatory interventions"
            ]
        ),
        "actionable_catalyst": Noul(
            instructions="Does the context present a concrete, verifiable catalyst with a clear short-to-medium term trading or investment thesis?"
        ),
        "regulatory_or_execution_risk": Noul(
            instructions="Does the 24h context highlight significant regulatory scrutiny, execution roadblocks, or insider selling that warrants caution?"
        ),
        "social_hype_level": Choice(
            instructions="Assess whether the social media / tweet commentary represents grounded fundamental analysis vs speculative retail hype.",
            criteria={
                "grounded": "Discussion centers on verified financial metrics, balance sheets, and institutional data",
                "mixed": "Mix of factual analysis and momentum trading sentiment",
                "speculative": "Dominated by rumors, meme hype, FOMO, or unverified claims"
            }
        )
    }

    response = client.system_one(state=state, questions=questions, model="jev-latest")

    bias_ans = response.choices["market_bias"]
    mat_ans = response.scores["materiality"]
    act_ans = response.nouls["actionable_catalyst"]
    risk_ans = response.nouls["regulatory_or_execution_risk"]
    hype_ans = response.choices["social_hype_level"]

    # Calculate expected directional bias value [-2.0 to +2.0] across Jev's probability distribution
    probs = bias_ans.probabilities or {}
    p_sb = probs.get("strong_bullish", 0.0)
    p_mb = probs.get("moderate_bullish", 0.0)
    p_neu = probs.get("neutral_or_mixed", 0.0)
    p_mbe = probs.get("moderate_bearish", 0.0)
    p_sbe = probs.get("strong_bearish", 0.0)

    bias_expected_value = (2.0 * p_sb) + (1.0 * p_mb) + (0.0 * p_neu) - (1.0 * p_mbe) - (2.0 * p_sbe)

    # Materiality score is 0.0 to 3.0
    materiality_score = float(mat_ans.score) if mat_ans.score is not None else 1.0

    # Risk factor (0.0 to 1.0)
    risk_prob = float(risk_ans.noul)

    # Actionable catalyst (0.0 to 1.0)
    actionable_prob = float(act_ans.noul)

    # Composite Scoring Formulation:
    # 1. Base magnitude scaled by materiality (higher materiality amplifies impact)
    # 2. Risk penalty dampens bullish bias or amplifies bearish bias
    # 3. Actionable probability scales execution confidence
    materiality_factor = 1.0 + (0.25 * materiality_score)
    risk_factor = 1.0 - (0.35 * risk_prob)
    actionable_factor = 0.65 + (0.35 * actionable_prob)

    composite_score = bias_expected_value * materiality_factor * risk_factor * actionable_factor

    # Assign Recommendation Tiers
    if composite_score >= 1.25 and actionable_prob >= 0.70 and risk_prob <= 0.40:
        rec_tier = "STRONG BUY"
    elif composite_score >= 0.45:
        rec_tier = "BUY"
    elif composite_score <= -1.10 and risk_prob >= 0.60:
        rec_tier = "STRONG SELL"
    elif composite_score <= -0.35:
        rec_tier = "UNDERWEIGHT / REDUCE"
    else:
        rec_tier = "HOLD / WATCH"

    # Distill key catalysts and risk points
    key_catalysts = [news[0]]
    if len(news) > 1:
        key_catalysts.append(news[1])

    risks = []
    if risk_prob > 0.35:
        for t in tweets + news:
            if any(k in t.lower() for k in ["caution", "probe", "nhtsa", "miss", "valuation", "insider", "risk", "delay"]):
                risks.append(t)
                break
    if not risks:
        risks.append("Macro interest rate volatility and general market rotation.")

    rationale = (
        f"Jev assessed {bias_ans.choice.replace('_', ' ').title()} bias with {bias_ans.confidence*100:.0f}% confidence. "
        f"Materiality is {materiality_score:.2f}/3.0 with {actionable_prob*100:.0f}% actionable probability. "
        f"Composite score is {composite_score:+.2f} after factoring {risk_prob*100:.0f}% risk overhang."
    )

    return StockRecommendation(
        ticker=ticker,
        company=company,
        sector=sector,
        recommendation=rec_tier,
        composite_score=round(composite_score, 2),
        confidence=round(bias_ans.confidence, 2),
        directional_bias=bias_ans.choice,
        bias_probabilities={k: round(v, 3) for k, v in probs.items()},
        materiality_score=round(materiality_score, 2),
        actionable_catalyst_prob=round(actionable_prob, 2),
        risk_factor_prob=round(risk_prob, 2),
        hype_profile=hype_ans.choice,
        key_catalysts=key_catalysts,
        risks_and_headwinds=risks,
        rationale=rationale
    )


def main():
    from feed_data import FEED_ITEMS

    print("=" * 80)
    print("📈 TYPE-SAFE STOCK EXCHANGE RECOMMENDATION SYSTEM (JEV-1.13)")
    print("   Evaluating Last 24 Hours News & Social Discourse via System One Judgments")
    print("=" * 80)

    client = TypeSafeClient()
    results: List[StockRecommendation] = []

    for item in FEED_ITEMS:
        print(f"[*] Analyzing {item['ticker']} ({item['company']})...")
        rec = evaluate_ticker(client, item)
        results.append(rec)

    # Sort results by composite score descending
    results.sort(key=lambda r: r.composite_score, reverse=True)

    print("\n" + "=" * 80)
    print(f"{'TICKER':<8} {'RECOMMENDATION':<20} {'SCORE':<8} {'CONF':<8} {'MATERIALITY':<12} {'HYPE'}")
    print("-" * 80)
    for r in results:
        print(
            f"{r.ticker:<8} {r.recommendation:<20} {r.composite_score:+0.2f}    "
            f"{r.confidence:0.2f}     {r.materiality_score:0.2f}/3.0      {r.hype_profile}"
        )
    print("=" * 80)

    # Save to JSON
    output_path = "/config/dev/jev/recommendations_latest.json"
    with open(output_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"\n[✓] Detailed report saved to {output_path}")


if __name__ == "__main__":
    main()
