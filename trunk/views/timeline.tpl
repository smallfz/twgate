<!-- timeline page -->
%include _header_timeline title=title
%include _user_menu
%include _timeline_menu

<h1>{{ title }}</h1>

<div class='block'>

{{! form_result }}

%if tw_user:
	<div class='userinfo'>
		<div class='icon'><img src="{{! tw_user['profile_image_url'] }}" border='0' /></div>
		<div class='screen_name'>{{ tw_user['screen_name'] }}</div>
		<div class='name'>{{ tw_user['name'] }}</div>
		<div class='fo_state'>
			following: {{ tw_user['friends_count'] }}, 
			followers: {{ tw_user['followers_count'] }}			
		</div>
		<div class='desc'>{{ tw_user['description'] }}</div>
		<div class='link'>{{ tw_user['url'] }}</div>
		<div class='follow'>
%if tw_user['following']:
	<script language='javascript'>function unfo(userid){
	if(confirm("Are you sure?")){ location.href="/unfollow/"+userid; } }
	</script>
	Following <a href='javascript:unfo({{tw_user['id']}});'>Unfollow</a>
%else:
	<a href='/follow/{{tw_user['id']}}'>Follow</a>
%end
		</div>
	</div>
%end

<p><span id='span_new_items_count'>
%if reloaded:
{{ reloaded }} new posts.
%end
</span></p>

%if posts:
<form id='replyform' method='post' action='/timeline/reply'>
	<input type='hidden' name='pid' value='' />
	<input type='hidden' name='screen_name' value='' />
	<input type='hidden' name='channel' value='{{ channel }}' />
</form>
<form id='rtform' method='post' action='/timeline/retweet'>
	<input type='hidden' name='pid' value='' />
	<input type='hidden' name='channel' value='{{ channel }}' />
%if tw_user:
	<input type='hidden' name='tw_userid' value='{{ tw_user['id'] }}' />
%end
</form>
%include _posts.tpl posts=posts

%if refresh_enabled:
<script language='javascript'>
var channel={{ channel }};
$(document).ready(function(){
	//__t = window.setInterval(check_new_posts, 1000 * 30);
	var func=function(){
		try{ get_new_posts(channel); }catch(e){}
	};
	var __t = window.setInterval(func, 1000 * 30);
});
</script>
%end
%end

%if pagemark:
	<div class='pagemark'>{{! pagemark }}</div>
%end
</div>


%include _user_bottom
