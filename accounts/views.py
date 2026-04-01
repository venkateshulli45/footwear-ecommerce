from urllib.parse import urlencode

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def _safe_redirect_path(request):
    nxt = request.POST.get('next') or request.GET.get('next')
    if nxt and url_has_allowed_host_and_scheme(
        nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return nxt
    return '/'


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(_safe_redirect_path(request))
        messages.info(request, 'Invalid credentials')
        nxt = request.POST.get('next')
        if nxt:
            return redirect(f"{reverse('login')}?{urlencode({'next': nxt})}")
        return redirect('login')
    return render(request, 'login.html')

def register(request):
    if request.method=="POST":
        first_name =request.POST['first_name']
        last_name =request.POST['last_name']
        username =request.POST['username']
        email =request.POST['email']
        password1 =request.POST['password1']
        password2 =request.POST['password2']
        
        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,"username already exists try with another")
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,"This email already have an account")
                return redirect('register')
            else:
                user =User.objects.create_user(username=username,password=password1,email=email,first_name=first_name,last_name=last_name)
                user.save();
                print('User Created')
                return redirect('login')
                
        else:
            messages.info(request,"password not match")
            return redirect('register')
        return redirect('/')
    else:
        return render(request,'register.html')
    
def logout(request):
    auth.logout(request)
    return redirect('/')