from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import Salary, Expense, Budget, ExpenseCategory, InvestmentSuggestion, MonthlyReport
from .forms import UserRegistrationForm, LoginForm, SalaryForm, ExpenseForm, BudgetForm
from .ai_integration import AISuggestionEngine
from .utils import calculate_financial_metrics, generate_chart_data

# Landing Page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker_app/landing.html')

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to your financial dashboard.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'tracker_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'tracker_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

# Dashboard View
@login_required
def dashboard(request):
    # Get current month data
    current_month = timezone.now().replace(day=1)
    
    # Get salary for current month
    salary = Salary.objects.filter(
        user=request.user,
        month__month=current_month.month,
        month__year=current_month.year
    ).first()
    
    # Get expenses for current month
    expenses = Expense.objects.filter(
        user=request.user,
        expense_date__month=current_month.month,
        expense_date__year=current_month.year
    )
    
    # Get budgets for current month
    budgets = Budget.objects.filter(
        user=request.user,
        month__month=current_month.month,
        month__year=current_month.year
    )
    
    # Calculate totals
    total_expenses = expenses.aggregate(total=Sum('expense_amount'))['total'] or 0
    remaining_balance = (salary.salary_amount if salary else 0) - total_expenses
    
    # Calculate budget usage
    budget_alerts = []
    for budget in budgets:
        category_expenses = expenses.filter(
            expense_category=budget.category
        ).aggregate(total=Sum('expense_amount'))['total'] or 0
        
        usage_percentage = (category_expenses / budget.budget_limit * 100) if budget.budget_limit > 0 else 0
        
        if usage_percentage >= 90:
            alert_level = 'danger'
        elif usage_percentage >= 70:
            alert_level = 'warning'
        else:
            alert_level = 'success'
        
        budget_alerts.append({
            'category': budget.category.name,
            'used': category_expenses,
            'limit': budget.budget_limit,
            'percentage': usage_percentage,
            'alert': alert_level
        })
    
    # Recent expenses
    recent_expenses = expenses.order_by('-expense_date')[:5]
    
    # Financial metrics
    metrics = calculate_financial_metrics(request.user, current_month)
    
    context = {
        'salary': salary,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'budget_alerts': budget_alerts,
        'recent_expenses': recent_expenses,
        'metrics': metrics,
        'current_month': current_month.strftime('%B %Y'),
    }
    
    return render(request, 'tracker_app/dashboard.html', context)

@login_required
def salary_management(request):
    salaries = Salary.objects.filter(user=request.user).order_by('-month')
    
    # Calculate statistics
    salary_stats = {
        'current_salary': None,
        'average_salary': 0,
        'growth_percentage': 0,
        'first_salary': None,
        'last_salary': None,
        'total_salaries': salaries.count(),
    }
    
    if salaries.exists():
        salary_stats['first_salary'] = salaries.last()  # Oldest
        salary_stats['last_salary'] = salaries.first()  # Latest (current)
        salary_stats['current_salary'] = salaries.first()
        
        # Calculate average of last 6 months
        last_six = salaries[:6]
        if last_six:
            total = sum(s.salary_amount for s in last_six)
            salary_stats['average_salary'] = total / len(last_six)
        
        # Calculate growth percentage
        if salary_stats['first_salary'] and salary_stats['last_salary']:
            if salary_stats['first_salary'].salary_amount > 0:
                growth = ((salary_stats['last_salary'].salary_amount - 
                          salary_stats['first_salary'].salary_amount) / 
                         salary_stats['first_salary'].salary_amount) * 100
                salary_stats['growth_percentage'] = round(growth, 2)
    
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.user = request.user
            
            # Check if salary already exists for this month
            existing = Salary.objects.filter(
                user=request.user,
                month__month=salary.month.month,
                month__year=salary.month.year
            ).first()
            
            if existing:
                existing.salary_amount = salary.salary_amount
                existing.currency = salary.currency
                existing.save()
                messages.success(request, 'Salary updated successfully!')
            else:
                salary.save()
                messages.success(request, 'Salary added successfully!')
            
            return redirect('salary_management')
    else:
        form = SalaryForm()
    
    context = {
        'form': form,
        'salaries': salaries,
        'stats': salary_stats,
        'current_month': timezone.now().replace(day=1),
    }
    
    return render(request, 'tracker_app/salary.html', context)
# Expense Management
@login_required
def expense_management(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    categories = ExpenseCategory.objects.all()
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_management')
    else:
        form = ExpenseForm()
    
    return render(request, 'tracker_app/expenses.html', {
        'form': form,
        'expenses': expenses,
        'categories': categories
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_management')
    else:
        form = ExpenseForm()
    
    return render(request, 'tracker_app/add_expense.html', {'form': form})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_management')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'tracker_app/add_expense.html', {'form': form, 'edit': True})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expense_management')

# Budget Management
@login_required
def budget_management(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-month')
    categories = ExpenseCategory.objects.all()
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            
            # Check if budget exists for this category and month
            existing = Budget.objects.filter(
                user=request.user,
                category=budget.category,
                month__month=budget.month.month,
                month__year=budget.month.year
            ).first()
            
            if existing:
                existing.budget_limit = budget.budget_limit
                existing.save()
                messages.success(request, 'Budget updated successfully!')
            else:
                budget.save()
                messages.success(request, 'Budget set successfully!')
            
            return redirect('budget_management')
    else:
        form = BudgetForm()
    
    return render(request, 'tracker_app/budget.html', {
        'form': form,
        'budgets': budgets,
        'categories': categories
    })

# Analytics View

@login_required
def analytics_view(request):
    current_month = timezone.now().replace(day=1)

    monthly_data = []
    total_salary_sum = 0
    total_expenses_sum = 0

    # Last 6 months analytics
    for i in range(6):
        month = current_month - timedelta(days=30 * i)

        salary_obj = Salary.objects.filter(
            user=request.user,
            month__month=month.month,
            month__year=month.year
        ).first()

        salary_amount = salary_obj.salary_amount if salary_obj else 0

        expenses = Expense.objects.filter(
            user=request.user,
            expense_date__month=month.month,
            expense_date__year=month.year
        ).aggregate(total=Sum('expense_amount'))['total'] or 0

        savings = salary_amount - expenses

        if salary_amount > 0:
            savings_percent = round((savings / salary_amount) * 100, 1)
        else:
            savings_percent = None

        total_salary_sum += salary_amount
        total_expenses_sum += expenses

        monthly_data.append({
            'month': month.strftime('%b %Y'),
            'salary': salary_amount,
            'expenses': expenses,
            'savings': savings,
            'savings_percent': savings_percent,
        })

    # Overall savings rate
    if total_salary_sum > 0:
        savings_rate = round(
            ((total_salary_sum - total_expenses_sum) / total_salary_sum) * 100, 1
        )
    else:
        savings_rate = 0.0

    avg_monthly_expense = round(total_expenses_sum / len(monthly_data), 2) if monthly_data else 0

    # Category breakdown (current month)
    category_data = []
    categories = ExpenseCategory.objects.all()

    for category in categories:
        total = Expense.objects.filter(
            user=request.user,
            expense_category=category,
            expense_date__month=current_month.month,
            expense_date__year=current_month.year
        ).aggregate(total=Sum('expense_amount'))['total'] or 0

        if total > 0:
            category_data.append({
                'name': category.name,
                'value': float(total),
                'color': category.color,
            })

    chart_data = generate_chart_data(monthly_data, category_data)

    context = {
        'monthly_data': monthly_data,
        'category_data': category_data,
        'chart_data': json.dumps(chart_data),
        'current_month': current_month.strftime('%B %Y'),
        'total_expenses_6m': total_expenses_sum,
        'avg_monthly_expense': avg_monthly_expense,
        'savings_rate': savings_rate,
    }

    return render(request, 'tracker_app/analytics.html', context)

# AI Investment Insights
@login_required
def ai_insights_view(request):
    current_month = timezone.now().replace(day=1)
    
    # Get financial data
    salary = Salary.objects.filter(
        user=request.user,
        month__month=current_month.month,
        month__year=current_month.year
    ).first()
    
    expenses = Expense.objects.filter(
        user=request.user,
        expense_date__month=current_month.month,
        expense_date__year=current_month.year
    )
    
    total_expenses = expenses.aggregate(total=Sum('expense_amount'))['total'] or 0
    remaining_balance = (salary.salary_amount if salary else 0) - total_expenses
    
    # Get expense patterns
    expense_patterns = {}
    for expense in expenses:
        category = expense.expense_category.name if expense.expense_category else 'Other'
        if category not in expense_patterns:
            expense_patterns[category] = 0
        expense_patterns[category] += float(expense.expense_amount)
    
    # Get AI suggestions
    ai_engine = AISuggestionEngine()
    
    if request.method == 'POST':
        risk_profile = request.POST.get('risk_profile', 'Moderate')
        
        # Get investment suggestions
        investment_suggestions = ai_engine.get_investment_suggestions(
            remaining_balance,
            risk_profile,
            expense_patterns
        )
        
        # Get financial health analysis
        savings_rate = (remaining_balance / salary.salary_amount * 100) if salary and salary.salary_amount > 0 else 0
        financial_health = ai_engine.analyze_financial_health(
            salary.salary_amount if salary else 0,
            total_expenses,
            savings_rate,
            85  # Placeholder for budget adherence
        )
        
        # Save to database
        InvestmentSuggestion.objects.create(
            user=request.user,
            remaining_balance=remaining_balance,
            risk_profile=risk_profile,
            suggestions={'suggestions': investment_suggestions},
            financial_health_score=min(100, int(savings_rate * 2 + 30))
        )
        
        context = {
            'suggestions': investment_suggestions,
            'financial_health': financial_health,
            'remaining_balance': remaining_balance,
            'risk_profile': risk_profile,
            'generated': True
        }
        
        return render(request, 'tracker_app/ai_insights.html', context)
    
    # Get previous suggestions
    previous_suggestions = InvestmentSuggestion.objects.filter(
        user=request.user
    ).order_by('-generated_at')[:3]
    
    context = {
        'remaining_balance': remaining_balance,
        'previous_suggestions': previous_suggestions,
        'generated': False
    }
    
    return render(request, 'tracker_app/ai_insights.html', context)

# Monthly Summary
@login_required
def monthly_summary_view(request):
    current_month = timezone.now().replace(day=1)
    
    # Get or generate report
    report = MonthlyReport.objects.filter(
        user=request.user,
        month__month=current_month.month,
        month__year=current_month.year
    ).first()
    
    if not report:
        # Generate new report
        report = generate_monthly_report(request.user, current_month)
    
    context = {
        'report': report,
        'current_month': current_month.strftime('%B %Y'),
    }
    
    return render(request, 'tracker_app/monthly_summary.html', context)

def generate_monthly_report(user, month):
    """Generate monthly report with AI insights"""
    
    # Get financial data
    salary = Salary.objects.filter(
        user=user,
        month__month=month.month,
        month__year=month.year
    ).first()
    
    expenses = Expense.objects.filter(
        user=user,
        expense_date__month=month.month,
        expense_date__year=month.year
    )
    
    budgets = Budget.objects.filter(
        user=user,
        month__month=month.month,
        month__year=month.year
    )
    
    # Calculate totals
    total_salary = salary.salary_amount if salary else 0
    total_expenses = expenses.aggregate(total=Sum('expense_amount'))['total'] or 0
    remaining_balance = total_salary - total_expenses
    savings_rate = (remaining_balance / total_salary * 100) if total_salary > 0 else 0
    
    # Category breakdown
    category_breakdown = {}
    for expense in expenses:
        category = expense.expense_category.name if expense.expense_category else 'Other'
        if category not in category_breakdown:
            category_breakdown[category] = 0
        category_breakdown[category] += float(expense.expense_amount)
    
    # Budget status
    budget_status = []
    for budget in budgets:
        category_expenses = expenses.filter(
            expense_category=budget.category
        ).aggregate(total=Sum('expense_amount'))['total'] or 0
        
        budget_status.append({
            'category': budget.category.name,
            'allocated': float(budget.budget_limit),
            'spent': float(category_expenses),
            'remaining': float(budget.budget_limit - category_expenses),
            'percentage': (category_expenses / budget.budget_limit * 100) if budget.budget_limit > 0 else 0
        })
    
    # Get AI advice
    ai_engine = AISuggestionEngine()
    expense_patterns = {k: v for k, v in category_breakdown.items()}
    ai_advice = ai_engine.get_investment_suggestions(
        remaining_balance,
        'Moderate',
        expense_patterns
    )
    
    # Create report
    report = MonthlyReport.objects.create(
        user=user,
        month=month,
        total_salary=total_salary,
        total_expenses=total_expenses,
        remaining_balance=remaining_balance,
        savings_rate=savings_rate,
        category_breakdown=category_breakdown,
        budget_status=budget_status,
        ai_advice=ai_advice
    )
    
    return report