from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.landing_page, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('salary/', views.salary_management, name='salary_management'),
    path('expenses/', views.expense_management, name='expense_management'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('budget/', views.budget_management, name='budget_management'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('ai-insights/', views.ai_insights_view, name='ai_insights'),
    path('monthly-summary/', views.monthly_summary_view, name='monthly_summary'),
]