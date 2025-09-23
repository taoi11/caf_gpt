"""
PolicyFoo app URL configuration.
"""
from django.urls import path
from .views import ChatInterfaceView, router

app_name = 'policy_foo'

urlpatterns = [
    path('', ChatInterfaceView.as_view(), name='chat_interface'),
    path('api/chat/', router.PolicyRouterView.as_view(), name='chat_api'),
]
