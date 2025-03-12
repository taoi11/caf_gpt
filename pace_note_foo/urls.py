from django.urls import path
from .views import pace_notes_view

app_name = 'pace_note_foo'

urlpatterns = [
    path('', pace_notes_view, name='pace_notes'),
] 