# -*- coding: utf8 -*-
from bottle import request, response, redirect
from users import CookieUser

# this is a decoration: auth_required
def auth_required(permission=None):
	def make_handler(low_handler):
		def handler(*args, **argv):
			cu = CookieUser(request=request, response=response)
			if cu.authenticated:
				pass
			else:
				return redirect("/login")
			return low_handler(*args, **argv)
		return handler
	return make_handler
