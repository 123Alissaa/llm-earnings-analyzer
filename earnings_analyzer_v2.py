from groq import Groq
import json
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt

class EarningsAnalyzerV2:
    def __init__(self, api_key=None):
        self.client = Groq(api_key=api_key)
    
    # [Keep your existing analyze_transcript method - EXACT same code]
    def analyze_transcript(self, transcript_text, company_name, ticker):
        """
        Use Groq AI to analyze earnings call transcript
        """
    
        prompt = f"""You are an expert quantitative analyst specializing in earnings call analysis.

    Analyze this earnings call transcript for {company_name} ({ticker}).

    TRANSCRIPT:
    {transcript_text[:4000]}

    Provide your analysis in the following JSON format:
    {{
        "sentiment_score": <number from -10 to +10, where -10 is very bearish and +10 is very bullish>,
        "sentiment_explanation": "<2-3 sentence explanation of the sentiment>",
        "key_metrics": {{
            "revenue": "<mentioned revenue figures>",
            "eps": "<earnings per share>",
            "guidance": "<forward guidance if mentioned>"
        }},
        "risk_factors": ["<list of 3-5 key risks mentioned>"],
        "management_tone": "<one word: confident/cautious/defensive/optimistic>",
        "recommendation": "<BUY/HOLD/SELL>",
        "recommendation_rationale": "<2-3 sentence investment thesis>",
        "key_quotes": ["<2-3 most important quotes from management>"]
    }}

    Respond ONLY with the JSON object, no other text."""
    
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
        
            # Extract text from response
            analysis_text = response.choices[0].message.content
        
            # Clean up any markdown code blocks if present
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
        
            # Parse JSON
            analysis = json.loads(analysis_text)
        
            return analysis
        
        except Exception as e:
            print(f"Error in analysis: {e}")
            print(f"Raw response: {analysis_text if 'analysis_text' in locals() else 'No response'}")
            return None
    
    def get_stock_reaction(self, ticker, earnings_date):
        """Get stock price reaction around earnings date"""
        start_date = earnings_date - timedelta(days=5)
        end_date = earnings_date + timedelta(days=5)
        
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if stock_data.empty:
                print(f"No stock data available for {ticker}")
                return None
            
            pre_price = stock_data['Close'].iloc[0]
            post_price = stock_data['Close'].iloc[-1]
            price_change = ((post_price - pre_price) / pre_price) * 100
            
            return {
                'pre_earnings_price': float(pre_price.iloc[0]),
                'post_earnings_price': float(post_price.iloc[0]),
                'price_change_pct': float(price_change.iloc[0]),
                'stock_data': stock_data
            }
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None
    
    def compare_sentiment_vs_price(self, sentiment_score, price_change_pct):
        """Compare LLM sentiment vs actual price reaction"""
        if (sentiment_score > 0 and price_change_pct > 0) or \
           (sentiment_score < 0 and price_change_pct < 0):
            alignment = "ALIGNED ✓"
            accuracy = "Sentiment and price moved in same direction"
        else:
            alignment = "MISALIGNED ✗"
            accuracy = "Sentiment and price moved in opposite directions"
        
        return {
            'alignment': alignment,
            'accuracy': accuracy,
            'sentiment_direction': 'Positive' if sentiment_score > 0 else 'Negative',
            'price_direction': 'Up' if price_change_pct > 0 else 'Down',
            'sentiment_magnitude': abs(sentiment_score),
            'price_magnitude': abs(price_change_pct)
        }
    
    def visualize_reaction(self, stock_data, sentiment_score, ticker, earnings_date):
        """Create visualization of stock reaction"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Price chart
        ax1.plot(stock_data.index, stock_data['Close'], marker='o', linewidth=2, color='#2E86AB')
        ax1.axvline(x=earnings_date, color='red', linestyle='--', linewidth=2, label='Earnings Date')
        ax1.set_title(f'{ticker} Stock Price Around Earnings', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Sentiment gauge
        color = 'green' if sentiment_score > 0 else 'red'
        ax2.barh(['LLM Sentiment'], [sentiment_score], color=color, alpha=0.7)
        ax2.set_xlim(-10, 10)
        ax2.set_xlabel('Sentiment Score', fontsize=12)
        ax2.axvline(x=0, color='black', linewidth=1)
        ax2.set_title('LLM Sentiment Analysis', fontsize=14, fontweight='bold')
        ax2.text(sentiment_score, 0, f' {sentiment_score:.1f}', 
                va='center', ha='left' if sentiment_score > 0 else 'right',
                fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        filename = f'{ticker}_earnings_analysis.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\nVisualization saved as: {filename}")
        plt.show()
        return filename
    
    def generate_full_report(self, analysis, company_name, ticker, stock_reaction, comparison):
        """Generate comprehensive report with sentiment and price analysis"""
        if not analysis:
            return "Analysis failed."
        
        report = f"""
{'='*80}
EARNINGS CALL ANALYSIS REPORT WITH PRICE VALIDATION
{'='*80}
Company: {company_name} ({ticker})
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*80}

OVERALL SENTIMENT: {analysis['sentiment_score']}/10
{analysis['sentiment_explanation']}

MANAGEMENT TONE: {analysis['management_tone'].upper()}

KEY FINANCIAL METRICS:
- Revenue: {analysis['key_metrics'].get('revenue', 'N/A')}
- EPS: {analysis['key_metrics'].get('eps', 'N/A')}
- Guidance: {analysis['key_metrics'].get('guidance', 'N/A')}

RISK FACTORS IDENTIFIED:
"""
        for i, risk in enumerate(analysis['risk_factors'], 1):
            report += f"  {i}. {risk}\n"
        
        report += f"""
INVESTMENT RECOMMENDATION: {analysis['recommendation']}

RATIONALE:
{analysis['recommendation_rationale']}

KEY MANAGEMENT QUOTES:
"""
        for i, quote in enumerate(analysis['key_quotes'], 1):
            report += f'  {i}. "{quote}"\n'
        
        if stock_reaction and comparison:
            report += f"""
{'='*80}
SENTIMENT vs ACTUAL PRICE MOVEMENT VALIDATION
{'='*80}

PREDICTIONS:
- LLM Sentiment Score: {analysis['sentiment_score']}/10 ({comparison['sentiment_direction']})
- Sentiment Magnitude: {comparison['sentiment_magnitude']:.1f}

ACTUAL RESULTS:
- Stock Price Change: {stock_reaction['price_change_pct']:.2f}% ({comparison['price_direction']})
- Pre-Earnings Price: ${stock_reaction['pre_earnings_price']:.2f}
- Post-Earnings Price: ${stock_reaction['post_earnings_price']:.2f}

VALIDATION:
- Alignment: {comparison['alignment']}
- Assessment: {comparison['accuracy']}

ACCURACY ANALYSIS:
"""
            if comparison['alignment'] == "ALIGNED ✓":
                report += "✓ The LLM correctly predicted the market direction!\n"
                report += f"  The model showed {comparison['sentiment_direction'].lower()} sentiment "
                report += f"and the stock moved {comparison['price_direction'].lower()}.\n"
            else:
                report += "✗ The LLM prediction did not align with market reaction.\n"
                report += f"  The model showed {comparison['sentiment_direction'].lower()} sentiment "
                report += f"but the stock moved {comparison['price_direction'].lower()}.\n"
                report += "  This could indicate:\n"
                report += "    - Market had already priced in the news\n"
                report += "    - External market factors dominated\n"
                report += "    - Expectations vs reality mismatch\n"
        
        report += f"\n{'='*80}\n"
        return report


if __name__ == "__main__":
    # CONFIGURATION
    TICKER = "JPM"
    COMPANY_NAME = "JPMorgan Chase & Co."
    EARNINGS_DATE = datetime(2025, 1 , 15)  # UPDATE THIS
    
    print(f"Analyzing {COMPANY_NAME} ({TICKER}) earnings call...")
    
    # Read transcript
    with open('jpm_transcript.txt', 'r') as f:
        transcript = f.read()
    
    # Initialize
    analyzer = EarningsAnalyzerV2()
    
    # Step 1: LLM Analysis
    analysis = analyzer.analyze_transcript(transcript, COMPANY_NAME, TICKER)
    sentiment_score = analysis['sentiment_score']
    
    # Step 2: Get Stock Data
    stock_reaction = analyzer.get_stock_reaction(TICKER, EARNINGS_DATE)
    price_change = stock_reaction['price_change_pct']
    
    # Step 3: Compare
    comparison = analyzer.compare_sentiment_vs_price(sentiment_score, price_change)
    
    # Step 4: Visualize
    viz_file = analyzer.visualize_reaction(
        stock_reaction['stock_data'],
        sentiment_score,
        TICKER,
        EARNINGS_DATE
    )
    
    # Step 5: Generate Report
    report = analyzer.generate_full_report(
        analysis, COMPANY_NAME, TICKER, 
        stock_reaction, comparison
    )
    
    print(report)
    
    # Save
    with open(f"earnings_report_v2_{TICKER}_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
        f.write(report)