"""
PaceNoteFoo app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'pacenote_foo'

urlpatterns = [
    path('', views.ChatInterfaceView.as_view(), name='chat_interface'),
    path('api/search/', views.RagSearchView.as_view(), name='rag_search'),
] 