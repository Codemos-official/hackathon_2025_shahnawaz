from datetime import datetime, timedelta
from django.db.models import Sum, Avg
from .models import Expense, Salary, Budget

def calculate_financial_metrics(user, current_month):
    """Calculate various financial metrics for dashboard"""
    
    # Current month expenses
    current_expenses = Expense.objects.filter(
        user=user,
        expense_date__month=current_month.month,
        expense_date__year=current_month.year
    ).aggregate(total=Sum('expense_amount'))['total'] or 0
    
    # Previous month expenses
    prev_month = current_month - timedelta(days=30)
    prev_expenses = Expense.objects.filter(
        user=user,
        expense_date__month=prev_month.month,
        expense_date__year=prev_month.year
    ).aggregate(total=Sum('expense_amount'))['total'] or 0
    
    # Calculate percentage change
    if prev_expenses > 0:
        expense_change = ((current_expenses - prev_expenses) / prev_expenses * 100)
    else:
        expense_change = 0
    
    # Average daily spending
    days_in_month = 30  # approximation
    avg_daily_spending = current_expenses / days_in_month if days_in_month > 0 else 0
    
    # Budget adherence
    budgets = Budget.objects.filter(
        user=user,
        month__month=current_month.month,
        month__year=current_month.year
    )
    
    total_budget = sum(budget.budget_limit for budget in budgets)
    budget_adherence = (total_budget - current_expenses) / total_budget * 100 if total_budget > 0 else 0
    
    return {
        'current_expenses': current_expenses,
        'prev_expenses': prev_expenses,
        'expense_change': expense_change,
        'avg_daily_spending': avg_daily_spending,
        'budget_adherence': budget_adherence,
        'total_budget': total_budget,
    }

def generate_chart_data(monthly_data, category_data):
    """Generate data for charts in analytics"""
    
    chart_data = {
        'line_chart': {
            'labels': [data['month'] for data in monthly_data],
            'salary_data': [float(data['salary']) for data in monthly_data],
            'expense_data': [float(data['expenses']) for data in monthly_data],
        },
        'pie_chart': {
            'labels': [data['name'] for data in category_data],
            'data': [data['value'] for data in category_data],
            'colors': [data['color'] for data in category_data],
        }
    }
    
    return chart_data

def format_currency(amount):
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def get_financial_health_score(user, month):
    """Calculate financial health score (0-100)"""
    
    salary = Salary.objects.filter(
        user=user,
        month__month=month.month,
        month__year=month.year
    ).first()
    
    expenses = Expense.objects.filter(
        user=user,
        expense_date__month=month.month,
        expense_date__year=month.year
    ).aggregate(total=Sum('expense_amount'))['total'] or 0
    
    if not salary or salary.salary_amount == 0:
        return 0
    
    savings = salary.salary_amount - expenses
    savings_rate = (savings / salary.salary_amount) * 100
    
    # Score components
    savings_score = min(savings_rate * 2, 40)  # 40% weight
    budget_score = 30  # Placeholder - would calculate from budget adherence
    diversity_score = 20  # Placeholder - would calculate from expense diversity
    consistency_score = 10  # Placeholder - would calculate from consistency
    
    total_score = savings_score + budget_score + diversity_score + consistency_score
    
    return min(int(total_score), 100)