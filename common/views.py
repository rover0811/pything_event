from django.shortcuts import render
from presentations.models import Presentation
from events.models import Event

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def posts(request):
    posts = Presentation.objects.select_related('presenter', 'event').order_by('-created_at')[:10]
    return render(request, 'posts.html', {'posts': posts})

def events(request):
    events = Event.objects.select_related('location').order_by('event_date', 'start_time')
    return render(request, 'events.html', {'events': events})

def people(request):
    return render(request, 'people.html') 