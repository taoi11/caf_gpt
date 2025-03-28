"""
PolicyFoo app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'policy_foo'

urlpatterns = [
    path('', views.ChatInterfaceView.as_view(), name='chat_interface'),
    path('documents/', views.DocumentSearchView.as_view(), name='document_search'),
    path('api/retrieve/', views.PolicyRetrieverView.as_view(), name='policy_retriever'),
    path('api/rate-limits/', views.RateLimitsView.as_view(), name='rate_limits'),
]
