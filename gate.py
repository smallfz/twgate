#!/usr/bin/python
# -*- coding: utf8 -*-

from bottle import run, route, abort, redirect, view, static_file
from bottle import get, post, request, response
from bottle import debug
import os
from widgets import *
from users import UserDb, CookieUser
from twitter import *
from auth import *
from apiproxy import *

debug(True)

@route("/static/:path#.+#")
def staticfiles(path):
	return static_file(path, root="./static")

@route("/favicon.ico")
def get_favicon():
	return static_file("favicon.ico", root="./static")

@route("/")
@view("main")
def index():
	username = ''
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		username = cu.username
	return dict(title="Welcome to TwGate.", user=username)


class ClientInfoPackage(object):	
	def __init__(self, key='', secret=''):
		self.key = key
		self.secret = secret

@post("/clientinfo")
@get("/clientinfo")
@view("user_clientinfo")
@auth_required()
def clientinfo_settings():
	cu = CookieUser(request=request, response=response)
	form = Form()
	settings = ClientInfoPackage()
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		if user is not None:
			clientinfo = service.get_user_clientinfo(user['id'])
			if clientinfo is not None:
				settings.key = clientinfo['consumer_key']
				settings.secret = clientinfo['consumer_secret']
			#form.msg = 'errmsg: %s' % service.errmsg
			if len(request.POST)>0:
				post_settings = ClientInfoPackage()
				post_settings.key = request.POST.get('consumer_key') or ''
				post_settings.secret = request.POST.get('consumer_secret') or ''
				if post_settings.key == settings.key and post_settings.secret == settings.secret:
					form.success = True
					form.msg = "客户端设置已保存。"
				else:
					service.set_user_clientinfo(user['id'], post_settings.key, post_settings.secret)
					service.clear_tokens(user['id'])
					form.success = True
					form.msg = "客户端设置已成功修改。你需要对新的客户端进行授权。"
					settings = post_settings
		else:
			form.msg = "Failed to load user's info."
	else:
		form.msg = "You should login first."
	return {'form_result': form, 'clientinfo': settings}

@post("/change_password")
@get("/change_password")
@view("change_password")
@auth_required()
def change_password():
	form = Form()
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		if len(request.forms)>0:
			current_password = request.forms.get('current_password')
			new_password = request.forms.get('new_password')
			new_password_r = request.forms.get('new_password_r')
			if current_password is None:
				current_password = ''

			service = UserDb()
			user = service.get_user(cu.uid)
			if user is not None:
				if new_password is not None and new_password_r is not None:
					if new_password == new_password_r:
						if user['passhash'].lower() == service.password_hash(current_password).lower():
							service.change_password(cu.uid, new_password)
							form.msg = '密码已成功修改。'
							form.success = True
						else:
							form.msg = '当前密码不正确。'
					else:
						form.msg = '请确认新密码两次输入一致。'
	else:
		form.msg = '必须登录才能进行本操作。'
	return dict(form_result=form)


@route("/welcome")
@view("user_main")
@auth_required()
def welcome():
	cu = CookieUser(request=request, response=response)
	apiurl=''
	search_api_url=''
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		if user is not None:
			sessionkey = user['sessionkey']
			if len(sessionkey)>0:
				apiurl = 'https://%s/api/%s/' % ('twip.bluemask.net', sessionkey)
				search_api_url = 'https://%s/searchapi/%s/' % ('twip.bluemask.net', sessionkey)
	return dict(title="Welcome to TwGate.", username=cu.username, user_api_url=apiurl, search_api_url=search_api_url)

@get("/logout")
def logout():
	cu = CookieUser(request=request, response=response)
	cu.clear()
	redirect('/')
	return ''

@get("/login")
@post("/login")
@view("login")
def login():
	form = Form()
	if len(request.forms)>0:
		email = request.forms.get('email')
		password = request.forms.get('password')
		service = UserDb()
		user = service.login(email, password)
		if user is not None:
			form.msg = '登录成功'
			form.success = True
			cu = CookieUser(request=request, response=response)
			cu.save(user['id'], user['username'], keep=True)
			# form.msg = '\n'.join(['%s: %s' % (k,v) for k,v in user.iteritems()])
			redirect('/welcome')
		else:
			form.msg = '用户名或者密码有错。'
	return dict(title="登录", form_result = form)
	
@post("/register")
@view("register")
def register_do():
	form = Form()
	if len(request.forms)>0:
		email = request.forms.get('email')
		password = request.forms.get('password')
		password_r = request.forms.get('password_r')
		if email is None or email == '':
			form.msg = '请填写你的Email地址。'
		elif len(password)<=0 or len(password_r)<=0:
			form.msg = '请填写密码，并确认两次输入保持一致。'
		elif password != password_r:
			form.msg = '两次密码输入不一致。'
		else:
			service = UserDb()
			if service.register(email, password):
				form.msg = '注册成功！'
				form.success = True
			else:
				form.msg = '注册失败(%s)' % service.errmsg
	else:
		pass
	return dict(title='注册新用户', form_result=form)

@get("/register")
@view("register")
def register():
	form = Form()
	return dict(title="新用户注册", form_result=form)


if __name__=='__main__':
	run(port=8081, reloader=True)



