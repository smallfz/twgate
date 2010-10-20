<!-- timeline posts -->
<div id='div_posts'>
	<span id='post_split'></span>
% index = 0
% for p in posts:
% if index==0:
<input type='hidden' id='txt_since_id' name='txt_since_id' value='{{ p['id'] }}' />
% end
<div class='post'>
	<div class='post-user'><a href='/timeline/user/{{p['user']['id']}}' style='color:#{{! p['user']['profile_link_color']}};'>{{! p['user']['screen_name'] }}</a></div>
	<div class='post-date'>{{! p['created_at'] }}</div>
	<div class='post-client'>from {{! p['source'] }}</div>
	<div class='post-handlers'>
		<a href="javascript:reply({{p['id']}}, '{{p['user']['screen_name']}}');" class='reply'>Reply</a>
		<a href="javascript:retweet({{p['id']}});" class='rt'>Retweet</a>
	</div>
	<div class='post-text'>{{! p['text'] }}</div>
</div>
% index += 1
% end
</div>
