<!-- user main page -->
%include _header title="欢迎登录"
%include _user_menu

<h1>欢迎登录，{{ username }}</h1>

<script language='javascript'>
function revoke(){
	if(!confirm('Are you sure?')){ return; }
	location.href="/sessions/revoke";
}
</script>
<div class='block'>
%if user_api_url:
	<p>你的个人API地址： <font color='#ccff66'>{{ user_api_url }}</font></p>
	<p>Search-API地址： <font color='#ccff66'>{{ search_api_url }}</font></p>
	<p>
		如果要停止授权本服务为你提供API转发，你可以<a href="javascript:revoke();">吊销授权</a>&raquo;
	</p>
	<p>
		<span class='success'><a href='/timeline'>View tweets &raquo;</a></span>
	</p>
%else:
	你需要授权本服务访问你的Twitter账户（OAuth授权方式），<a href="/sessions/req">开始验证&raquo;</a>
%end
</div>

%include _user_bottom
