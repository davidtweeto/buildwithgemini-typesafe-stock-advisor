"""
24-Hour Market News and Social Discourse Feed Data
Aggregated across financial newswires, earnings calendars, and investor social sentiment (Twitter/X).
"""

FEED_ITEMS = [
    {
        "ticker": "NVDA",
        "company": "Nvidia Corporation",
        "sector": "Semiconductors & AI Hardware",
        "last_24h_news": [
            "Nvidia Q2 FY2027 revenue surged 106% YoY to $96.2B, outperforming Wall Street consensus across all segments.",
            "Forward guidance for Q3 projected at $108B with management forecasting ~70% revenue expansion into FY2028 on severe compute supply shortages.",
            "Reports confirmed advanced discussions to acquire AI developer platform Hugging Face for $13B-$14B to solidify software ecosystem moat.",
            "Key Wall Street investment banks raised 12-month price targets citing Blackwell and Rubin architecture demand exceeding capacity through 2027."
        ],
        "last_24h_tweets": [
            "$NVDA guidance at $108B is absurd. Even with Treasury yields fluctuating, their gross margins (75%+) make them an unmatched cash generation machine.",
            "Blackwell production ramp is entirely sold out for the next 5 quarters. Every hyperscaler is in line. Long and adding on any intraday dip.",
            "Unconfirmed rumors of the Hugging Face acquisition would be the biggest dev ecosystem lock-in since GitHub was bought by Microsoft.",
            "Bear tweet: Valuation at these heights leaves zero room for execution hiccups or any export restriction escalation."
        ]
    },
    {
        "ticker": "MU",
        "company": "Micron Technology, Inc.",
        "sector": "Memory & Storage Semiconductors",
        "last_24h_news": [
            "Micron shares surged over 5.2% to cross the $1,000 benchmark, breaking out past key technical resistance levels ahead of Q4 earnings.",
            "Micron is scheduled to report fiscal Q4 and full-year 2026 earnings on September 30, with analysts modeling record HBM3e/HBM4 revenue.",
            "High-Bandwidth Memory (HBM) contract pricing saw another double-digit quarter-over-quarter hike driven by hyperscaler AI cluster buildouts.",
            "Industry supply checks indicate DRAM and HBM wafer allocation is fully booked through calendar year 2027, triggering structural gross margin expansion."
        ],
        "last_24h_tweets": [
            "$MU breakout is real. Earnings on Sept 30 will be the print of the season. HBM capacity constraint is the biggest bottleneck in AI right now.",
            "Micron trades at one of the lowest forward PEG ratios in mega-cap semiconductors despite having the fastest earnings acceleration.",
            "Traders loading up on Oct calls ahead of the earnings report next week. Volume profile is heavily skewed bullish.",
            "Cautious note: What if Micron guides conservatively due to cleanroom expansion capex? Still holding core position."
        ]
    },
    {
        "ticker": "META",
        "company": "Meta Platforms, Inc.",
        "sector": "Digital Advertising & Autonomous AI",
        "last_24h_news": [
            "Meta launched its autonomous 'Muse AI' agent workflow across enterprise apps, drawing widespread praise for benchmark reasoning efficiency.",
            "Digital advertising revenue showed resilient double-digit growth, with AI-driven ad targeting conversion rates rising 18% quarter-over-quarter.",
            "Meta confirmed expanding custom MTIA silicon deployment in data centers to lower operational compute costs.",
            "Brokerage upgrade from Overweight to Top Pick with revised $820 target, noting Meta's transition from AI capex spender to immediate AI monetizer."
        ],
        "last_24h_tweets": [
            "The Muse AI agent rollout is shockingly polished. Meta's ability to ship consumer and enterprise AI at scale is unmatched.",
            "$META free cash flow yield remains top-tier among mega-caps. Ad engine is subsidizing long-term AI bets without margin degradation.",
            "Social media engagement across Instagram Reels and Threads continues taking market share from rivals.",
            "Skeptical take: Metaverse/Reality Labs segment still burning $4B+ per quarter, keep an eye on upcoming capex commentary."
        ]
    },
    {
        "ticker": "TSLA",
        "company": "Tesla, Inc.",
        "sector": "Automotive & Autonomous Systems",
        "last_24h_news": [
            "National Highway Traffic Safety Administration (NHTSA) formally requested detailed documentation regarding the Cybercab robotaxi design without pedals and steering wheel.",
            "Tesla confirmed an official unveiling event scheduled for October 1 for the next-generation Tesla Roadster halo performance vehicle.",
            "Q3 vehicle delivery forecasts revised downward by several automotive analysts due to stiff EV price competition in Europe and China.",
            "SEC Form 4 filings revealed routine insider stock sales by CFO Vaibhav Taneja under pre-arranged 10b5-1 trading plans."
        ],
        "last_24h_tweets": [
            "$TSLA NHTSA inquiry is just regulatory theater. Tesla will have Cybercab testing permits resolved. Oct 1 Roadster event will be electric!",
            "Caution on Tesla here. Deliveries coming next week might miss consensus, and the NHTSA probe on pedal-free Cybercab introduces real launch delay risk.",
            "Tesla has lagged all year while NVDA, META and MU rip to all-time highs. Opportunity cost is killing bulls.",
            "Autonomous FSD v13 rollout shows massive disengagement improvements, but commercial robotaxi monetization is still 18-24 months out."
        ]
    },
    {
        "ticker": "JPM",
        "company": "JPMorgan Chase & Co.",
        "sector": "Financials & Banking",
        "last_24h_news": [
            "JPMorgan shares pulled back 0.8% in recent sessions, exerting a minor drag on the Dow Jones Industrial Average.",
            "CEO Jamie Dimon highlighted macroeconomic caution at a financial summit, pointing to persistent geopolitical friction and shifting Treasury yields.",
            "Net interest income expectations for commercial banking were trimmed slightly as loan demand cooled amid elevated corporate borrowing rates.",
            "Investment banking pipeline remains solid with equity underwriting rebounding, though M&A advisory closures face extended antitrust review times."
        ],
        "last_24h_tweets": [
            "$JPM taking a breather after an enormous multi-month run. Financials seeing capital rotation into semiconductor momentum.",
            "Jamie Dimon once again playing the prudent risk manager. Nothing fundamentally broken, but growth multiple is capped here.",
            "Dividend yield and buyback cushion remain pristine. Great defensive sleep-well-at-night hold, not a fast momentum trade.",
            "Watching the 10-year yield closely—if the curve steepens further, JPM will find immediate support."
        ]
    },
    {
        "ticker": "VLO",
        "company": "Valero Energy Corporation",
        "sector": "Energy & Petroleum Refining",
        "last_24h_news": [
            "Valero Energy surged to a fresh 52-week high with trading volume 40% above 30-day average.",
            "Global crude oil benchmarks (Brent) declined on rising non-OPEC supply, while regional refined product cracks widened significantly.",
            "Valero reported near-record throughput utilization across its Gulf Coast refining complex, benefiting from low feedstock costs.",
            "Board of Directors authorized an expanded share repurchase program and increased quarterly dividend distribution."
        ],
        "last_24h_tweets": [
            "$VLO printing money right now. Crude prices dropping while gasoline and diesel margins stay firm is the dream setup for independent refiners.",
            "New 52-week highs with heavy institutional accumulation. Energy rotation is quietly playing out under the surface.",
            "Refining margins are cyclical, but Valero's balance sheet has virtually zero net debt and high shareholder return yield.",
            "Taking partial profits above the breakout level; watch out for potential demand destruction if macro manufacturing data softens."
        ]
    }
]
