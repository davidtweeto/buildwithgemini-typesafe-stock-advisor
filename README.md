# TypeSafe AI Stock Exchange Intelligence (Jev-1.13)

A real-time financial market intelligence and decision engine powered by **TypeSafe AI's System One model (Jev-1.13)**.

The application ingests 24-hour financial news headlines and trader discourse (StockTwits, Seeking Alpha, Google News) to generate typed judgments, directional probability distributions, materiality scores, actionable catalyst probabilities, and composite risk-adjusted recommendation badges (**STRONG BUY**, **BUY**, **NEUTRAL**, **REDUCE**, **SELL**).

---

## ⚡ Architecture & How It Works

Traditional LLM setups rely on unpredictable freeform text generation and brittle JSON parsing. This application uses TypeSafe AI's **Jev-1.13 System One decision model**, executing parallel structured evaluations:

1. **Market Bias (`market_bias`)**: Computes calibrated probability distributions across `bullish`, `bearish`, and `neutral_or_mixed`.
2. **Materiality Score (`materiality`)**: Scores event impact from 0.0 to 3.0 (Low, Moderate, Substantial, Critical).
3. **Actionable Catalyst Detection (`actionable_catalyst`)**: Evaluates the probability of an immediate catalyst affecting the stock.
4. **Risk Overhang Assessment (`regulatory_or_execution_risk`)**: Measures downside risk factors such as regulatory investigations, margin squeeze, or execution delays.
5. **Composite Expected Value Scoring**: Combines directional probabilities, materiality, catalyst strength, and risk overhang into a normalized composite score from `-3.0` to `+3.0`.

---

## 🚀 Features

* **Automated 24h Feed Ingestion**: Fetches breaking news wires and trader sentiment feeds using ticker symbols.
* **Interactive Web Application**: Fast single-page application with responsive desktop and mobile layouts (iOS & Android friendly).
* **Live On-Demand Evaluation**: Enter any ticker symbol to auto-fetch its latest 24h dossier and run instant Jev evaluations.
* **Pre-Evaluated Dossiers**: Cached evaluations for leading equities (NVDA, TSLA, AAPL, AMZN, AMD, MSFT, META, JPM, VLO, AOM).
* **Cloud Run Ready**: Containerized with Docker and ready for serverless deployment on Google Cloud Run.

---

## 🛠️ Project Structure

```text
├── app.py                      # FastAPI server & responsive web interface
├── stock_recommender.py        # TypeSafe Jev-1.13 composite evaluation logic
├── live_feed.py                # 24-hour RSS / financial news & social ingestion pipeline
├── feed_data.py                # Pre-assembled market dossiers & testing data
├── generate_report.py          # Static HTML dashboard generator
├── recommendations_latest.json # Cached evaluation outputs & probability distributions
├── Dockerfile                  # Container definition for Cloud Run / Docker
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variable configuration template
```

---

## 📦 Setup & Installation

### 1. Prerequisites
* Python 3.11 or 3.12
* A TypeSafe AI API key (from [typesafe.ai](https://typesafe.ai))

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 3. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Add your TypeSafe API key:
```env
TYPESAFE_API_KEY=your_typesafe_api_key_here
```

---

## 💻 Running Locally

Start the FastAPI application:
```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```
Open your browser at `http://localhost:8080`.

---

## 🐳 Docker & Cloud Deployment

### Build and Run with Docker
```bash
docker build -t typesafe-stock-advisor .
docker run -p 8080:8080 -e TYPESAFE_API_KEY=your_typesafe_api_key_here typesafe-stock-advisor
```

### Deploy to Google Cloud Run
```bash
gcloud run deploy typesafe-stock-advisor \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars TYPESAFE_API_KEY=your_typesafe_api_key_here
```

---

## 📄 License
MIT License
