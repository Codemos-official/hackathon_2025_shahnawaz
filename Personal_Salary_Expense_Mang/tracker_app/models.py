from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    month = models.DateField()
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=10, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']
    
    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')}"

class ExpenseCategory(models.Model):
    CATEGORY_CHOICES = [
        ('Food & Dining', 'Food & Dining'),
        ('Transportation', 'Transportation'),
        ('Shopping', 'Shopping'),
        ('Entertainment', 'Entertainment'),
        ('Bills & Utilities', 'Bills & Utilities'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Rent & Mortgage', 'Rent & Mortgage'),
        ('Investment', 'Investment'),
        ('Savings', 'Savings'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='fa-receipt')
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    expense_name = models.CharField(max_length=200)
    expense_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)
    expense_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.expense_name} - ₹{self.expense_amount}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    month = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'category', 'month')
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ₹{self.budget_limit}"

class InvestmentSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_suggestions')
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    risk_profile = models.CharField(max_length=20, choices=[
        ('Conservative', 'Conservative'),
        ('Moderate', 'Moderate'),
        ('Aggressive', 'Aggressive')
    ])
    suggestions = models.JSONField()
    financial_health_score = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.generated_at.strftime('%Y-%m-%d')}"

class MonthlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_reports')
    month = models.DateField()
    total_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    savings_rate = models.DecimalField(max_digits=5, decimal_places=2)
    category_breakdown = models.JSONField()
    budget_status = models.JSONField()
    ai_advice = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'month')
    
    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')}"