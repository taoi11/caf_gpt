"""
PolicyFoo app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'policy_foo'

urlpatterns = [
    path('', views.ChatInterfaceView.as_view(), name='chat_interface'),
    path('api/rate-limits/', views.RateLimitsView.as_view(), name='rate_limits'),
]
