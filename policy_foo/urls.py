"""
PolicyFoo app URL configuration.
"""
from django.urls import path
from .views import ChatInterfaceView, router
from .views.rate_limits import RateLimitsView
from core.views import rate_limit_view

app_name = 'policy_foo'

urlpatterns = [
    path('', ChatInterfaceView.as_view(), name='chat_interface'),
    path('api/rate-limits/', RateLimitsView.as_view(), name='rate_limits'),
    path('api/chat/', router.PolicyRouterView.as_view(), name='chat_api'),
    path('rate-limit/', rate_limit_view, name='rate_limit'),
]
