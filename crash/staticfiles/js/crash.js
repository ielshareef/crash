// Google Analytics  -->
var _gaq=_gaq||[];_gaq.push(["_setAccount","UA-33605835-1"]);_gaq.push(["_trackPageview"]);(function(){var b=document.createElement("script");b.type="text/javascript";b.async=true;b.src=("https:"==document.location.protocol?"https://ssl":"http://www")+".google-analytics.com/ga.js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(b,a)})();
// Cross Site Request Forgery, CSRF Protection
jQuery(document).ajaxSend(function(c,f,b){function a(g){var l=null;if(document.cookie&&document.cookie!=""){var k=document.cookie.split(";");for(var j=0;j<k.length;j++){var h=jQuery.trim(k[j]);if(h.substring(0,g.length+1)==(g+"=")){l=decodeURIComponent(h.substring(g.length+1));break}}}return l}function e(h){var j=document.location.host;var k=document.location.protocol;var i="//"+j;var g=k+i;return(h==g||h.slice(0,g.length+1)==g+"/")||(h==i||h.slice(0,i.length+1)==i+"/")||!(/^(\/\/|http:|https:).*/.test(h))}function d(g){return(/^(GET|HEAD|OPTIONS|TRACE)$/.test(g))}if(!d(b.type)&&e(b.url)){f.setRequestHeader("X-CSRFToken",a("csrftoken"))}});

// Crash utility class

CRASH = window.CRASH || {
	fbLogout: function() {
		FB.logout(function(res) {
			window.location = '/';
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
					$.post("/get_username", {'uid': response[0]['uid']}, function(data) {
						if (data == 'void') {
							window.location = '/';
						} else {
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