import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class AISuggestionEngine:
    def __init__(self):
        self.ai_provider = getattr(settings, 'AI_PROVIDER', 'fallback')

        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.openai_org = getattr(settings, 'OPENAI_ORG', None)

        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    # =====================================================
    # INVESTMENT SUGGESTIONS
    # =====================================================
    def get_investment_suggestions(self, remaining_balance, risk_profile, expense_patterns):
        prompt = f"""
User Balance: ₹{remaining_balance}
Risk Profile: {risk_profile}
Expense Pattern: {expense_patterns}

Give India-specific, beginner-friendly investment advice.
"""

        try:
            if self.ai_provider == 'openai' and self.openai_api_key:
                return self._openai(prompt)
            elif self.ai_provider == 'gemini' and self.gemini_api_key:
                return self._gemini(prompt)
            else:
                return self._fallback_investment(remaining_balance)
        except Exception as e:
            logger.error(e)
            return self._fallback_investment(remaining_balance)

    # =====================================================
    # 🔥 FINANCIAL HEALTH ANALYSIS (THIS FIXES YOUR ERROR)
    # =====================================================
    def analyze_financial_health(self, salary, expenses, savings_rate, budget_adherence):
        prompt = f"""
Monthly Salary: ₹{salary}
Monthly Expenses: ₹{expenses}
Savings Rate: {savings_rate}%
Budget Adherence: {budget_adherence}%

Give financial health score and improvement tips.
"""

        try:
            if self.ai_provider == 'openai' and self.openai_api_key:
                return self._openai(prompt)
            elif self.ai_provider == 'gemini' and self.gemini_api_key:
                return self._gemini(prompt)
            else:
                return self._fallback_health(salary, expenses, savings_rate)
        except Exception as e:
            logger.error(e)
            return self._fallback_health(salary, expenses, savings_rate)

    # =====================================================
    # OPENAI
    # =====================================================
    def _openai(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a financial advisor for Indian users."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1200
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        return None

    # =====================================================
    # GEMINI
    # =====================================================
    def _gemini(self, prompt):
        url = f"{self.gemini_url}?key={self.gemini_api_key}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        return None

    # =====================================================
    # FALLBACK METHODS
    # =====================================================
    def _fallback_investment(self, balance):
        return f"""
SAFE: PPF, FD
MODERATE: Index Funds
GROWTH: SIP in Mutual Funds

Start investing ₹{min(balance * 0.3, 5000):.0f}/month
"""

    def _fallback_health(self, salary, expenses, savings_rate):
        score = min(100, int(savings_rate * 2 + 40))
        return f"""
FINANCIAL HEALTH SCORE: {score}/100

Improve by:
• Increase savings to 20%
• Reduce unnecessary expenses
• Build emergency fund
"""
