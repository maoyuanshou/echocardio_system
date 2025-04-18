from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import User  # 你的自定义用户模型
from django.contrib import messages


def home(request):
    return render(request, 'core/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'core/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            user = User.objects.create_user(username=username, password=password, role=role)
            messages.success(request, '注册成功')
            return redirect('login')
    return render(request, 'core/register.html')
