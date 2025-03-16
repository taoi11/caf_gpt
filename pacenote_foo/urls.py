"""
PaceNoteFoo app URL configuration.
"""
from django.urls import path
from . import views

app_name = 'pacenote_foo'

urlpatterns = [
    path('', views.PaceNoteView.as_view(), name='pace_notes'),
    path('api/generate-pace-note/', views.PaceNoteGeneratorView.as_view(), name='generate_pace_note'),
]
