"""
Core app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
] 