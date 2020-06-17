from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.contrib import auth


# 登录表单
class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名',
                                        widget=widgets.TextInput(
                                            {'placeholder': '请输入用户名或邮箱', 'class': 'login-modal-user form-control',
                                             'autocomplete': 'off'}),
                                        required=True)
    password = forms.CharField(label='密码',
                               widget=widgets.TextInput(
                                   {'placeholder': '请输入密码', 'type': 'password',
                                    'class': 'login-modal-password form-control',
                                    'autocomplete': 'new-password'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if user:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
                else:
                    raise forms.ValidationError('用户名或密码不正确')
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


# 注册表单
class RegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               widget=widgets.TextInput(
                                   {'placeholder': '请输入用户名', 'class': 'login-modal-user form-control',
                                    'autocomplete': 'off'}),
                               required=True)
    password = forms.CharField(label='密码',
                               widget=widgets.TextInput(
                                   {'placeholder': '请输入密码', 'type': 'password',
                                    'class': 'login-modal-password form-control',
                                    'autocomplete': 'new-password'}))
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput({
                                 'class': 'login-modal-email form-control',
                                 'placeholder': '请输入邮箱', 'type': 'email',
                                 'autocomplete': 'off'
                             }))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput({
                                            'class': 'form-control',
                                            'placeholder': '点击“发送验证码”发送到邮箱',
                                            'autocomplete': 'off'
                                        }))


# 修改昵称
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(label='新的昵称',
                                   max_length=20,
                                   widget=widgets.TextInput(
                                       {'placeholder': '请输入新的昵称', 'class': 'login-modal-user form-control',
                                        'autocomplete': 'off'}),
                                   required=True)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError('新的昵称不能为空')
        already_use = User.objects.filter(profile__nickname=nickname_new).exists()
        if already_use:
            raise forms.ValidationError('该昵称已被使用')
        return nickname_new


# 绑定邮箱
class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput({
                                 'class': 'form-control',
                                 'placeholder': '请输入正确的邮箱', 'type': 'email',
                                 'autocomplete': 'off'
                             }))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput({
                                            'class': 'form-control',
                                            'placeholder': '点击“发送验证码”发送到邮箱',
                                            'autocomplete': 'off'
                                        }))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断用户是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定邮箱')

        # 判断验证码
        code = self.request.session.get(self.cleaned_data['email'], '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code.upper() == verification_code.upper()):
            raise forms.ValidationError('验证码不正确')

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定!')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


# 修改邮箱
class ChangeEmailForm(forms.Form):
    password = forms.CharField(label='密码',
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': '请输入密码', 'type': 'password',
                                   'autocomplete': 'off'
                               }))
    email = forms.EmailField(label='新邮箱',
                             widget=forms.EmailInput({
                                 'class': 'form-control',
                                 'placeholder': '请输入正确的邮箱', 'type': 'email',
                                 'autocomplete': 'off'
                             }))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput({
                                            'class': 'form-control',
                                            'placeholder': '点击“发送验证码”发送到邮箱',
                                            'autocomplete': 'off'
                                        }))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断验证码
        email = self.request.POST.get('email', '')
        code = self.request.session.get(email, '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code.upper() == verification_code.upper()):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定!')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data['verification_code']
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

    def clean_password(self):
        password = self.cleaned_data['password']
        user = auth.authenticate(username=self.request.user.username, password=password)
        if user is None:
            raise forms.ValidationError('密码不正确')
        return password


# 修改密码
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='原密码',
                                   widget=widgets.TextInput(
                                       {'placeholder': '请输入原密码', 'type': 'password',
                                        'class': 'login-modal-password form-control',
                                        'autocomplete': 'new-password'}))
    new_password = forms.CharField(label='新密码',
                                   widget=widgets.TextInput(
                                       {'placeholder': '请输入新密码', 'type': 'password',
                                        'class': 'login-modal-password form-control',
                                        'autocomplete': 'new-password'}))
    confirm_password = forms.CharField(label='再次输入新密码',
                                       widget=widgets.TextInput(
                                           {'placeholder': '再次输入新密码', 'type': 'password',
                                            'class': 'login-modal-password form-control',
                                            'autocomplete': 'new-password'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        old_password = self.cleaned_data.get('old_password', '')
        new_password = self.cleaned_data.get('new_password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if old_password == new_password and old_password != '':
            raise forms.ValidationError('新密码不可以与旧密码相同！')
        if new_password != confirm_password or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致！')
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('密码验证失败！')
        return old_password


# 忘记密码
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='绑定邮箱',
                             widget=forms.EmailInput({
                                 'class': 'form-control',
                                 'placeholder': '请输入账号绑定的邮箱', 'type': 'email',
                                 'autocomplete': 'off'
                             }))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput({
                                            'class': 'form-control',
                                            'placeholder': '点击“发送验证码”发送验证码到邮箱',
                                            'autocomplete': 'off'
                                        }))
    new_password = forms.CharField(label='新密码',
                                   widget=widgets.TextInput(
                                       {'placeholder': '请输入新密码', 'type': 'password',
                                        'class': 'login-modal-password form-control',
                                        'autocomplete': 'new-password'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在!')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码
        email = self.cleaned_data.get('email', '')
        code = self.request.session.get(email, '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code.upper() == verification_code.upper()):
            raise forms.ValidationError('验证码不正确')
        return verification_code
