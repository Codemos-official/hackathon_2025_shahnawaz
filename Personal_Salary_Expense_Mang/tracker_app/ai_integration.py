import requests
import logging
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class AISuggestionEngine:
    def __init__(self):
        self.ai_provider = getattr(settings, "AI_PROVIDER", "fallback")
        self.openai_api_key = getattr(settings, "OPENAI_API_KEY", None)
        self.gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)

        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-pro:generateContent"
        )

    # =====================================================
    # INVESTMENT SUGGESTIONS
    # =====================================================
    def get_investment_suggestions(self, remaining_balance, risk_profile, expense_patterns):
        balance = Decimal(remaining_balance)

        prompt = f"""
You are an Indian personal finance advisor.

User Details:
- Available Balance: ₹{balance}
- Risk Profile: {risk_profile}
- Expense Pattern: {expense_patterns}

Give a DETAILED, beginner-friendly answer with:
• amount
• reason
• expected return
• time horizon

Format strictly with headings.
"""

        try:
            if self.ai_provider in ("openai", "auto") and self.openai_api_key:
                try:
                    return self._openai(prompt)
                except Exception as e:
                    logger.warning(f"OpenAI failed: {e}")

            if self.ai_provider in ("gemini", "auto") and self.gemini_api_key:
                try:
                    return self._gemini(prompt)
                except Exception as e:
                    logger.warning(f"Gemini failed: {e}")

            return self._fallback_investment(balance, risk_profile)

        except Exception:
            return self._fallback_investment(balance, risk_profile)

    # =====================================================
    # FINANCIAL HEALTH (2 ARGUMENTS ONLY)
    # =====================================================
    def analyze_financial_health(self, salary, expenses):
        salary = Decimal(salary)
        expenses = Decimal(expenses)

        savings = salary - expenses
        savings_rate = (savings / salary) * Decimal("100") if salary > 0 else Decimal("0")

        return self._fallback_health(salary, expenses, savings_rate)

    # =====================================================
    # OPENAI
    # =====================================================
    def _openai(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an Indian financial advisor."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.6,
            "max_tokens": 1200,
        }

        response = requests.post(self.openai_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        raise Exception("OpenAI API failed")

    # =====================================================
    # GEMINI
    # =====================================================
    def _gemini(self, prompt):
        url = f"{self.gemini_url}?key={self.gemini_api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        raise Exception("Gemini API failed")

    # =====================================================
    # FALLBACK INVESTMENT (VERY DETAILED)
    # =====================================================
    def _fallback_investment(self, balance, risk_profile):
        q = Decimal("1")

        low = (balance * Decimal("0.40")).quantize(q, ROUND_HALF_UP)
        moderate = (balance * Decimal("0.35")).quantize(q, ROUND_HALF_UP)
        high = (balance * Decimal("0.25")).quantize(q, ROUND_HALF_UP)

        return f"""
FINANCIAL SUMMARY
=================
Available Balance : ₹{balance}
Risk Profile      : {risk_profile}

--------------------------------------------------
LOW RISK INVESTMENTS 🟢 (Capital Protection)
--------------------------------------------------
1️⃣ Fixed Deposit (FD)
• Amount           : ₹{low}
• Why              : Guaranteed returns, zero market risk
• Expected Return  : 5% – 6.5% annually
• Time Horizon     : 6 months – 3 years
• Suitable For     : Emergency & short-term safety

2️⃣ Public Provident Fund (PPF)
• Amount           : ₹{(low * Decimal("0.50")).quantize(q)}
• Why              : Tax-free + Government backed
• Expected Return  : ~7% annually
• Time Horizon     : 15 years
• Suitable For     : Long-term disciplined savings

--------------------------------------------------
MODERATE RISK INVESTMENTS 🟡 (Balanced Growth)
--------------------------------------------------
1️⃣ Index Mutual Fund (NIFTY 50 SIP)
• Amount           : ₹{moderate}
• Why              : Market growth with lower volatility
• Expected Return  : 10% – 12% annually
• Time Horizon     : 3 – 5 years
• Suitable For     : First-time investors

--------------------------------------------------
HIGH RISK / GROWTH OPTIONS 🔴 (Wealth Creation)
--------------------------------------------------
1️⃣ Equity Mutual Fund SIP
• Amount           : ₹{high}
• Why              : Higher growth potential
• Expected Return  : 12% – 15% annually
• Time Horizon     : 5+ years
• Suitable For     : Long-term wealth creation

--------------------------------------------------
SMART MONEY TIPS 💡
--------------------------------------------------
• Keep 6 months of expenses as emergency fund
• SIP is safer than lump sum for beginners
• Review investments every 6 months
• Increase SIP amount yearly with income growth

DISCLAIMER ⚠️
--------------------------------------------------
This is educational guidance, not registered financial advice.
"""

    # =====================================================
    # FALLBACK FINANCIAL HEALTH (DETAILED)
    # =====================================================
    def _fallback_health(self, salary, expenses, savings_rate):
        score = min(100, max(30, int((savings_rate * Decimal("2")) + Decimal("40"))))

        status = (
            "Excellent" if score >= 80 else
            "Good" if score >= 60 else
            "Needs Improvement"
        )

        return f"""
FINANCIAL HEALTH REPORT
======================
Monthly Income   : ₹{salary}
Monthly Expenses : ₹{expenses}
Savings Rate     : {savings_rate.quantize(Decimal("1"))}%

HEALTH SCORE
------------
Score  : {score}/100
Status : {status}

INTERPRETATION
--------------
• 80+  → Very strong financial discipline
• 60+  → Stable but can improve
• <60  → High risk, needs budgeting

IMPROVEMENT PLAN
----------------
• Save minimum 20% of income
• Track expenses weekly
• Avoid impulse spending
• Start SIP immediately
"""
