%include _header title="Welcome to TwGate"

<!-- main page -->

%if title:
	<h1>{{ title }}</h1>
%end
	https://twip.bluemask.net



	<div class='block'>
	<p>TwGate是一个Twitter API转发服务，本服务与客户端之间使用SSL通信。</p>
	<p>
		已注册用户请<a href="/login">点此登录&raquo;</a>
	</p>
	<p>
		或者<a href="/register">注册&raquo;</a>
	</p>
	</div>

	<div class='block'>
	</div>

%if user:
	<p>
	<span class='success'>当前用户： <strong>{{ user }}</strong> 已登录。 <a href='/welcome'>进入&raquo;</a></span>
	</p>
%end

  </body>
</html>
