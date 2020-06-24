import string
import random
import time
import threading
import urllib.request
import json
from smtplib import SMTPRecipientsRefused
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django.core.validators import validate_email
from urllib.parse import urlencode, parse_qs
from .models import Profile, OAuthRelationShip
from zrhblog import settings
from .forms import LoginForm, ChangeNicknameForm, BindEmailForm, ChangeEmailForm, ChangePasswordForm, ForgotPasswordForm


# 多线程发送邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.text,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
        )


# GitHub登录
def login_by_github(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if state != settings.GitHub_state:
        raise Exception('state error')
    # Access token
    params = {
        'client_id': settings.GitHub_APP_ID,
        'client_secret': settings.GitHub_APP_Secret,
        'code': code,
        'redirect_uri': settings.GitHub_Redirect,
    }
    response = urllib.request.urlopen('https://github.com/login/oauth/access_token?' + urlencode(params))
    data = response.read().decode('utf-8')
    access_token = parse_qs(data)['access_token'][0]
    # 用户标识id
    url = 'https://api.github.com/user'
    github_request = urllib.request.Request(url, headers={'Authorization': 'token ' + access_token})
    response = urllib.request.urlopen(github_request)
    data = response.read().decode('utf-8')
    node_id = json.loads(data)['node_id']

    # 判断node_id是否关联用户,已关联则直接登录
    if OAuthRelationShip.objects.filter(open_id=node_id, oauth_type=1).exists():
        relationship = OAuthRelationShip.objects.get(open_id=node_id, oauth_type=1)
        user = relationship.user
    else:
        # 未关联则创建用户,并关联Node_id
        username = str(int(time.time()))
        password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        nickname = json.loads(data)['name']
        user = User.objects.create_user(username, '', password)
        Profile.objects.get_or_create(user=user, nickname=nickname)
        relationship = OAuthRelationShip()
        relationship.user = user
        relationship.open_id = node_id
        relationship.oauth_type = 1
        relationship.save()
    # 登录
    auth.login(request, user)
    return redirect(reverse('home'))


# 检测表单中是否含有汉字
def check_chinese(*param):
    for item in param:
        for word in item:
            if u'\u4e00' <= word <= u'\u9fff':
                return True
    return False


# 使用模态框登录时在此处验证
def login_for_modal(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        data = dict()
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            data['status'] = 'SUCCESS'
        else:
            data['status'] = 'ERROR'
        return JsonResponse(data)


# 用户注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        pwd_again = request.POST.get('pwd_again', '').strip()
        email = request.POST.get('email', '').strip()
        if check_chinese(username, password, pwd_again, email):
            return render(request, 'user/register.html', {'reg_error': '不能含有中文'})
        if (username or password or pwd_again or email) == '':
            return render(request, 'user/register.html', {'reg_error': '请填写必要信息'})
        if User.objects.filter(username=username).exists():
            return render(request, 'user/register.html', {'reg_error': '用户名已存在'})
        if password != pwd_again:
            return render(request, 'user/register.html', {'reg_error': '两次输入的密码不一致'})
        if User.objects.filter(email=email).exists():
            return render(request, 'user/register.html', {'reg_error': '该邮箱已被注册'})
        # 创建用户
        user = User.objects.create_user(username, email, password)
        user.save()
        # 登录用户
        user = auth.authenticate(request, username=username, password=password)
        auth.login(request, user)
        return redirect(request.GET.get('from', reverse('home')))
    else:
        return render(request, 'user/register.html')


# 使用登录页面登录在此处验证
def login(request):
    if request.method == 'GET':
        return render(request, 'user/login.html')
    else:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
        else:
            return render(request, 'user/login.html', {'message': '用户名或密码错误'})


# 注销
def logout(request):
    auth.logout(request)
    redirect_to = request.GET.get('from')
    if (request.GET.get('from')).find('my_notifications'):
        redirect_to = reverse('home')
    return redirect(redirect_to, reverse('home'))


# 个人资料
def user_info(request):
    context = dict()
    return render(request, 'user/user_info.html', context)


# 修改昵称
def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = dict()
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'forms.html', context)


# 绑定邮箱
def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session[email]
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = dict()
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)


# 修改邮箱
def change_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':

        form = ChangeEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session[email]
            return redirect(redirect_to)
    else:
        form = ChangeEmailForm()

    context = dict()
    context['page_title'] = '修改邮箱'
    context['form_title'] = '修改邮箱'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)


# 发送验证码
def send_verification_code(request):
    email = request.GET.get('email', '')
    data = dict()
    try:
        # 判断邮箱是否有效
        validate_email(email)
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        request.session[email] = code
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['error'] = '验证码发送过于频繁'
        else:
            request.session[email] = code
            request.session['send_code_time'] = now
            # 发送邮件
            try:
                subject = '【zrhblog】账号安全'
                text = '验证码： %s' % code
                send_email = SendMail(subject, text, email)
                send_email.start()
                data['status'] = 'SUCCESS'
            except SMTPRecipientsRefused:
                data['error'] = '发送失败,请检查邮箱地址'
    except ValidationError:
        data['error'] = '邮箱无效！'
    return JsonResponse(data)


# 修改密码
def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = dict()
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '确定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'forms.html', context)


# 忘记密码
def forgot_password(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del request.session[email]
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = dict()
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '确定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)
