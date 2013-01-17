// Google Analytics  -->
var _gaq=_gaq||[];_gaq.push(["_setAccount","UA-33605835-1"]);_gaq.push(["_trackPageview"]);(function(){var b=document.createElement("script");b.type="text/javascript";b.async=true;b.src=("https:"==document.location.protocol?"https://ssl":"http://www")+".google-analytics.com/ga.js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(b,a)})();
// Cross Site Request Forgery, CSRF Protection
jQuery(document).ajaxSend(function(c,f,b){function a(g){var l=null;if(document.cookie&&document.cookie!=""){var k=document.cookie.split(";");for(var j=0;j<k.length;j++){var h=jQuery.trim(k[j]);if(h.substring(0,g.length+1)==(g+"=")){l=decodeURIComponent(h.substring(g.length+1));break}}}return l}function e(h){var j=document.location.host;var k=document.location.protocol;var i="//"+j;var g=k+i;return(h==g||h.slice(0,g.length+1)==g+"/")||(h==i||h.slice(0,i.length+1)==i+"/")||!(/^(\/\/|http:|https:).*/.test(h))}function d(g){return(/^(GET|HEAD|OPTIONS|TRACE)$/.test(g))}if(!d(b.type)&&e(b.url)){f.setRequestHeader("X-CSRFToken",a("csrftoken"))}});

$.cookie.raw = true;

// Crash utility class
CRASH = window.CRASH || {
	flushToken: function() {
		$.removeCookie('api_token', { path: '/' });
	},
	flushUser: function() {
		$.removeCookie('user_email', { path: '/' });
		$.removeCookie('user_uid', { path: '/' });
		$.removeCookie('user_name', { path: '/' });
		$.removeCookie('user_username', { path: '/' });
		$.removeCookie('validated_user', { path: '/' });
		CRASH.flushToken();
	},
	fbLogout: function() {
		FB.logout(function(res) {
			CRASH.flushUser();
			window.location = window.location.href;
		})
	},
	fbLogin: function() {
		FB.login(function(response) {
			if (response.authResponse) {
		     	_gaq.push(['_trackEvent', 'Facebook', 'login', 'successful']);
				var token = response.authResponse.accessToken;
		  		FB.api({
					method: 'fql.query',
					query: 'SELECT uid, username, email, first_name, last_name, name, pic_square_with_logo, birthday_date, hometown_location, current_location FROM user WHERE uid=me()'
				}, function(response) {
					_gaq.push(['_trackEvent', 'Facebook', 'user', response[0].name]);
					$.post("/get_username", {'email': response[0]['email']}, function(data) {
						$.cookie('validated_user', 'yes', { expires: 30*3600*1000, path: '/' });
						if (data == 'does_not_exist') {
							window.location = '/';
						} else {
							CRASH.flushToken();
							$.cookie('user_email', response[0]['email'], { expires: 30*3600*1000, path: '/' });
							$.cookie('user_uid', response[0]['uid'], { expires: 30*3600*1000, path: '/' });
							$.cookie('user_name', response[0]['name'], { expires: 30*3600*1000, path: '/' });
							$.cookie('user_username', data, { expires: 30*3600*1000, path: '/' });
							window.location = window.location.href;
						}
					});
		     	});
		   	} else {
		  		_gaq.push(['_trackEvent', 'Facebook', 'login', 'canceled']);
			}
		}, {scope: 'email, user_location, user_hometown, user_birthday, user_likes, publish_stream'});
	}
};

(function() {
	function forPlus(e) {
		e.preventDefault();
		if(!$.cookie('user_email')) {
			alert('Uh-oh, you need to sign in to Like a photo.');
		} else {
			var checkin = this.innerHTML;
			$('#loading_'+checkin).removeClass('hide');
			var that = this;
			$.post("/add_like", {'checkin': checkin}, function(data) {
				$('#checkin_likes_'+checkin).html(function() {
					this.innerHTML = parseInt(this.innerHTML) + 1;
					$('#loading_'+checkin).addClass('hide');
					$(that).addClass('minus');
					$(that).removeClass('plus');
				});
			});
			$(that).unbind('click');
			$(that).bind('click', forMinus);
		}
	}
	$('.plus').live('click', forPlus);
	
	function forMinus(e) {
		e.preventDefault();
		var checkin = this.innerHTML;
		$('#loading_'+checkin).removeClass('hide');
		var that = this;
		$.post("/delete_like", {'checkin': checkin}, function(data) {
			$('#checkin_likes_'+checkin).html(function() {
				this.innerHTML = parseInt(this.innerHTML) - 1;
				$('#loading_'+checkin).addClass('hide');
				$(that).removeClass('minus');
				$(that).addClass('plus');
			});
		});
		$(that).unbind('click');
		$(that).bind('click', forPlus);
	}
	$('.minus').live('click', forMinus);
})();