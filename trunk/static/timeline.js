// -------------------

function reply(pid, screen_name){
	var frm=document.getElementById('replyform');
	if(frm && pid>0){
		frm.pid.value = pid;
		if(screen_name){ frm.screen_name.value = screen_name; }
		frm.submit();
	}
}
function retweet(pid){
	var frm=document.getElementById('rtform');
	if(frm && pid>0 && confirm("Retweet this?")){
		frm.pid.value = pid;
		frm.submit();
	}
}

// --------------------


var create_post_div = function(container, objbefore, p){
	var pspan=document.createElement('span');
	//container.insertBefore(pspan, objbefore);
	container.appendChild(pspan);
	pspan.className='post';
	var span_u = document.createElement('span');
	pspan.appendChild(span_u);
	span_u.innerHTML="<a href='/timeline/user/"+p['user']['id']+"' style='color:#"+p['user']['profile_link_color']+";'>"+p['user']['screen_name']+"</a>";
	span_u.className="post-user";
	var span_date = document.createElement('span');
	pspan.appendChild(span_date);
	span_date.innerHTML=p["created_at"];
	span_date.className="post-date";
	var span_c = document.createElement('span');
	pspan.appendChild(span_c);
	span_c.innerHTML=p["source"];
	span_c.className="post-client";
	//
	var span_handlers = document.createElement('span');
	pspan.appendChild(span_handlers);
	span_handlers.className="post-handlers";
	var a_reply=document.createElement('a');
	span_handlers.appendChild(a_reply);
	a_reply.href="javascript:reply("+p['id']+", '"+p['user']['screen_name']+"');";
	a_reply.innerHTML='Reply';
	a_reply.className='reply';
	var a_rt=document.createElement('a');
	span_handlers.appendChild(a_rt);
	a_rt.href="javascript:retweet("+p['id']+");";
	a_rt.innerHTML='Retweet';
	a_rt.className='rt';
	//
	var span_text = document.createElement('span');
	pspan.appendChild(span_text);
	span_text.innerHTML=p["text"];
	span_text.className="post-text";
};
var get_new_posts = function(channel){
	var txt_sid=document.getElementById('txt_since_id');
	if(txt_sid){
		var sid=parseInt(txt_sid.value);
		if(isNaN(sid)){ sid=0; }
		var container=document.getElementById('div_posts');
		if(!container){
			return;
		}else{
			var posts_len=0;
			for(var j=0;j<container.childNodes.length;j++){ 
				if(container.childNodes[j].className=='post'){ posts_len++;} 
			}
			if(posts_len>150){
				location.href=location.href;
				return;
			}
		}
		//var channel=parseInt("{{ channel }}");
		if(isNaN(channel)){ channel=-1;}
		if(channel==0 || channel==1){
			var url=channel==0?'/timeline/since/'+sid:'/timeline/i/since/'+sid;
			$.get(url, function(posts){
				if(posts){
					var newitems = eval(posts);
					if(newitems){
						if(newitems.length){
							var ctl_split=document.getElementById('post_split');
							var new_ctl_split=document.createElement('span');
							container.insertBefore(new_ctl_split, ctl_split)
							var div_block = document.createElement('span');
							container.insertBefore(div_block, ctl_split);
							div_block.style.cssText="display:block; height:0px; overflow:hidden;";
							div_block.className="new_items_block";
							var max_id=0;
							for(var i=0;i<newitems.length;i++){
								create_post_div(div_block/*container*/, ctl_split, newitems[i]);
								if(newitems[i]['id'] > max_id){
									max_id = newitems[i]['id'];
								}
							}
							txt_sid.value = max_id;
							ctl_split.id = '';
							new_ctl_split.id = 'post_split';
							container.removeChild(ctl_split);
							//
							var h = div_block.scrollHeight, step=2, current_height=0;
							var t= null, finalCssText="display:block; border-bottom:1px solid #0099cc;";
							if(h>0){
								var bigger=function(){
										try{
										if(current_height<=h && current_height+step>h){
											if(t){ window.clearInterval(t); }
											div_block.style.cssText=finalCssText;
										}else{
											current_height += step;
											div_block.style.cssText="display:block; height:"+current_height+"px; overflow:hidden;";
											div_block.scrollTop=h - current_height;
											if(step<10){
												step=parseInt(1.5*step);
											}
										}
									}catch(e){
									}
								};
								t = window.setInterval(bigger, 50);
							}else{
								div_block.style.cssText=finalCssText;
							}
							//
							var nc=document.getElementById('span_new_items_count');
							if(nc){
								nc.innerHTML=newitems.length+" new posts."; 
								var fade=function(){ nc.innerHTML="&nbsp;"; };
								window.setTimeout(fade, 5000);
							}
						}
					}
				}
			});
		}
	}
};

var check_new_posts = function(channel){
	try{
	$.get('/timeline/fetchall', function(data){
		var count=parseInt(data);
		if(isNaN(count)){ count=0; }
		if(count>0){
			// location.href=location.href;
			get_new_posts(channel);
		}
	});
	}catch(e){}
}
