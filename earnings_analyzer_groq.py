from groq import Groq
import json
from datetime import datetime

class EarningsAnalyzer:
    def __init__(self, api_key=None):
        self.client = Groq(api_key=api_key)
    
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
    
    def generate_report(self, analysis, company_name, ticker):
        """Generate formatted report"""
        
        if not analysis:
            return "Analysis failed."
        
        report = f"""
{'='*80}
EARNINGS CALL ANALYSIS REPORT
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
        
        report += f"\n{'='*80}\n"
        
        return report

# Usage
if __name__ == "__main__":
    # Read transcript
    with open('sample_transcript.txt', 'r') as f:
        transcript = f.read()
    
    # Analyze (API key will come from environment variable)
    analyzer = EarningsAnalyzer()
    analysis = analyzer.analyze_transcript(
        transcript, 
        company_name="Coinbase Global, Inc.", 
        ticker="COIN"
    )
    
    # Generate report
    if analysis:
        report = analyzer.generate_report(analysis, "Coinbase Global, Inc.", "COIN")
        print(report)
        
        # Save to file
        with open(f"earnings_report_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(report)
        
        print("\nReport saved!")
    else:
        print("Analysis failed. Check your API key and transcript file.")