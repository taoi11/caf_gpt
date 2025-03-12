from django.shortcuts import render

def pace_notes_view(request):
    """
    View for the Pace Notes page.
    """
    return render(request, 'pace_notes.html') 