<!-- user main page -->
%include _header title="设置客户端信息"
%include _user_menu

<h2>设置客户端信息</h2>

<div class='block'>
	{{! form_result }}
	
	<form method='post' action=''>
	<p>Consumer key:<br />
		<input type="text" name="consumer_key" size="50" value="{{! clientinfo.key }}" /></p>
	<p>Consumer secret:<br />
		<input type="text" name="consumer_secret" size="50" value="{{! clientinfo.secret }}" /></p>
	<p><input type='submit' value='保存设定' /></p>
	</form>
	
</div>

%include _user_bottom
