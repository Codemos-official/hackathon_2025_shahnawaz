from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Salary, Expense, Budget, ExpenseCategory
from django.utils import timezone
import datetime
from datetime import date

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['month', 'salary_amount', 'currency']
        widgets = {
            'month': forms.DateInput(
                attrs={
                    'type': 'date',    
                    'class': 'form-control'
                }
            ),
            'salary_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'currency': forms.Select(
                attrs={'class': 'form-control'},
                choices=[('INR', '₹ INR'), ('USD', '$ USD')]
            ),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_name', 'expense_amount', 'expense_category', 'expense_date', 'description']
        widgets = {
            'expense_name': forms.TextInput(attrs={'class': 'form-control'}),
            'expense_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expense_category': forms.Select(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'budget_limit', 'month']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'budget_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'month': forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        }