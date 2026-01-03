from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Salary, Expense, Budget, ExpenseCategory, InvestmentSuggestion, MonthlyReport

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon']
    list_editable = ['color', 'icon']

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'salary_amount', 'currency', 'created_at']
    list_filter = ['month', 'currency']
    search_fields = ['user__username', 'user__email']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'expense_name', 'expense_amount', 'expense_category', 'expense_date']
    list_filter = ['expense_category', 'expense_date']
    search_fields = ['expense_name', 'user__username']
    date_hierarchy = 'expense_date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'budget_limit', 'month']
    list_filter = ['month', 'category']
    search_fields = ['user__username']

@admin.register(InvestmentSuggestion)
class InvestmentSuggestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'remaining_balance', 'risk_profile', 'financial_health_score', 'generated_at']
    list_filter = ['risk_profile', 'generated_at']
    readonly_fields = ['generated_at']

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'total_salary', 'total_expenses', 'remaining_balance', 'savings_rate']
    list_filter = ['month']
    readonly_fields = ['generated_at']