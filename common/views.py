from django.shortcuts import render, redirect
from presentations.models import Presentation
from events.models import Event
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User

User = get_user_model()

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

def presentations(request):
    presentations = Presentation.objects.select_related('presenter', 'event').order_by('-created_at')[:10]
    return render(request, 'presentations.html', {'presentations': presentations})

def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = '아이디 또는 비밀번호가 올바르지 않습니다.'
    return render(request, 'login.html', {'error_message': error_message, 'login_tab': True})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup_view(request):
    error_message = None
    success_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            error_message = '비밀번호가 일치하지 않습니다.'
        elif User.objects.filter(username=username).exists():
            error_message = '이미 존재하는 아이디입니다.'
        elif User.objects.filter(email=email).exists():
            error_message = '이미 사용 중인 이메일입니다.'
        else:
            User.objects.create_user(username=username, email=email, password=password1)
            return render(request, 'login.html', {
                'login_tab': True,
                'success_message': '회원가입이 완료되었습니다. 로그인 해주세요.'
            })
    return render(request, 'login.html', {'login_tab': False, 'error_message': error_message})

def mypage(request):
    return render(request, 'mypage.html') 