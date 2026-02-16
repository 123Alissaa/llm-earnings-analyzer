# LLM Earnings Call Analyzer

AI-powered financial analysis tool that automatically analyzes earnings call transcripts and generates investment insights using Large Language Models.

## Features

- **Sentiment Analysis**: Scores management tone from -10 (very bearish) to +10 (very bullish)
- **Financial Metrics Extraction**: Automatically pulls revenue, EPS, and guidance from transcripts
- **Risk Assessment**: Identifies 3-5 key risk factors mentioned by management
- **Investment Recommendations**: Generates BUY/HOLD/SELL recommendations with rationale
- **Key Quotes Extraction**: Highlights the most important management statements

## Example Output
```
OVERALL SENTIMENT: 8/10
Management expressed strong confidence in diversification strategy...

MANAGEMENT TONE: OPTIMISTIC

KEY FINANCIAL METRICS:
- Revenue: $7.2B (2025 full year)
- Subscription revenue: Up 5.5x from 2021 peak

INVESTMENT RECOMMENDATION: BUY
```

## Tech Stack

- **Python 3.x**
- **Groq API** (Llama 3.3 70B model)
- **JSON parsing** for structured output
- Natural Language Processing

## Installation
```bash
pip install groq
export GROQ_API_KEY='your-api-key'
```

## 💻 Usage
```bash
python earnings_analyzer_groq.py
```

## Use Cases

- Automated earnings call analysis for investment research
- Sentiment tracking across multiple quarters
- Comparative analysis of competitor earnings calls
- Risk factor monitoring over time

## Tested Companies

- Coinbase (COIN)
- Apple (AAPL)
- Tesla (TSLA)
- Microsoft (MSFT)


**Built as part of quantitative finance learning journey**
