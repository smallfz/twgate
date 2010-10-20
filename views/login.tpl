<!-- login page -->
%include _header title="登录"
<h1>用户登录</h1>

<div class='block'>
{{! form_result }}
%if not form_result.success:
	<form method="POST">
		<p>Email: <br /><input type='text' name='email' value='' /></p>
		<p>Password: <br /><input type='password' name='password' value='' /></p>
		<p>
			<input type='submit' value=' 登录 ' />
		</p>
	</form>
%end

</div>

%include _bottom
