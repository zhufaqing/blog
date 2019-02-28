from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms
import hashlib


def hash_code(s, salt='mysite'):  # 加点盐
	h = hashlib.sha256()
	s += salt
	h.update(s.encode())  # update方法只接收bytes类型
	return h.hexdigest()


def index(request):
	pass
	return render(request, 'users/index.html')


def login(request):
	# 不允许重复登录
	if request.session.get('is_login', None):
		return redirect('/index/')
	
	if request.method == "POST":
		# username = request.POST.get('username')
		# password = request.POST.get('password')
		login_form = forms.UserForm(request.POST)
		message = "所有字段都必须填写！"
		
		# if username and password:
		if login_form.is_valid():
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']
			# username = username.strip()
			
			try:
				user = models.User.objects.get(name=username)
				# if user.password == password:
				if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
					# 获取session
					request.session['is_login'] = True
					request.session['user_id'] = user.id
					request.session['user_name'] = user.name
					return redirect('/index/')
				else:
					message = "密码不正确!"
			except:
				message = "用户名不存在!"
		return render(request, 'users/login.html', locals())
	login_form = forms.UserForm()
	return render(request, 'users/login.html', locals())


def register(request):
	if request.session.get('is_login', None):
		# 登录状态不允许注册。你可以修改这条原则！
		return redirect("/index/")
	if request.method == "POST":
		register_form = forms.RegisterForm(request.POST)
		message = "请检查填写的内容！"
		if register_form.is_valid():  # 获取数据
			username = register_form.cleaned_data['username']
			password1 = register_form.cleaned_data['password1']
			password2 = register_form.cleaned_data['password2']
			email = register_form.cleaned_data['email']
			sex = register_form.cleaned_data['sex']
			if password1 != password2:  # 判断两次密码是否相同
				message = "两次输入的密码不同！"
				return render(request, 'users/register.html', locals())
			else:
				same_name_user = models.User.objects.filter(name=username)
				if same_name_user:  # 用户名唯一
					message = '用户已经存在，请重新选择用户名！'
					return render(request, 'users/register.html', locals())
				same_email_user = models.User.objects.filter(email=email)
				if same_email_user:  # 邮箱地址唯一
					message = '该邮箱地址已被注册，请使用别的邮箱！'
					return render(request, 'users/register.html', locals())
				
				# 当一切都OK的情况下，创建新用户
				
				new_user = models.User()
				new_user.name = username
				new_user.password = hash_code(password1)  # 使用加密密码
				new_user.email = email
				new_user.sex = sex
				new_user.save()
				return redirect('/login/')  # 自动跳转到登录页面
	register_form = forms.RegisterForm()
	return render(request, 'users/register.html', locals())


def logout(request):
	if not request.session.get('is_login', None):
		return redirect("/index/")
	request.session.flush()
	return redirect("/index/")
