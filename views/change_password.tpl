<!-- user main page -->
%include _header title="修改登录密码"
%include _user_menu

<h2>修改登录密码</h2>

<div class='block'>
{{! form_result }}

%if not form_result.success:
<form method='post'>
	<p>当前密码：<br />
		<input type='password' name='current_password' />
	</p>
	<p>新密码：<br />
		<input type='password' name='new_password' />
	</p>
	<p>重复新密码：<br />
		<input type='password' name='new_password_r' />
	</p>
	<p>
		<input type='submit' value='修改' />
	</p>
</form>
</div>
%end
%include _user_bottom
