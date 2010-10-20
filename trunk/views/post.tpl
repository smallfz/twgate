<!-- timeline page -->
%include _header title=title
%include _user_menu
%include _timeline_menu

<h1>{{ title }}</h1>

<div class='block'>
{{! form_result }}
%if not form_result.success:
	<form method='post' action='/timeline/i/add'>
		<textarea name='content' cols='60' rows='3'>{{ initial_text }}</textarea>
		<p>
			<input type='hidden' name='reply_post_id' value='{{ reply_post_id }}' />
			<input type='submit' value='发布' />
		</p>
	</form>
%end


</div>

%include _user_bottom
