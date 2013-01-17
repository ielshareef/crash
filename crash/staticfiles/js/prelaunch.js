(function() {		
	var selected_username = false;
	var selected_location = false;
	
	// Validate username in realtime
	$("#username").keyup(function() {
		var username = $("#username").val();
		if (username && /^[a-z0-9]+$/i.test(username)) {
			$.post("/check_username", {'username': username}, function(data) {
				data = $.parseJSON(data);
				if (data.error == 300) {
					$('#status').css('display', 'block');
					$('#status').css('color', 'red');
					$('#status').html('Taken!');
					selected_username = false;
				} else {
					$('#status').css('display', 'block');
					$('#status').css('color', '#cfe198');
					$('#status').html('Available!');
					selected_username = username;
				}
			});
		} else {
			$('#status').css('display', 'none');
			selected_username = false;
		}
	});
	
	// Manage textarea focus/blur actions
	$('#textarea').focus(function() {
		$(this).css('color', '#000');
	});
	
	$('#textarea').blur(function() {
		if (this.value == '') {
			$(this).css('color', '#ccc');
			this.value = "I just reserved my username on Crash, the coolest attraction discovery app on the planet.\n\nYou should too!";
		}
	});
	
	$("#myModal").bind("hide", function() {
		window.location = '/'+selected_username;
	});
	
	// Click to share on Facebook
	$('#shareOnFb').click(function() {
		var obj = {
			message     : $('#textarea').val(),
			link        : 'http://cra.sh/',
			picture     : 'http://fathomless-peak-7496.herokuapp.com/static/img/logo-white2.gif',
			name        : 'Crashworks Inc',
			description : 'Crash is a location-based attraction discovery app currently being incubated out of Idealab and launching Fall 2012.'
		};
		FB.api('/me/feed', 'post', obj, function(response) {
			if (!response || response.error) {
				_gaq.push(['_trackEvent', 'Facebook', 'share', 'Failure: ' + response.error.message]);
			} else {
				_gaq.push(['_trackEvent', 'Facebook', 'share', 'success: ' + $('#textarea').value]);
				$('#myModal').modal('hide');
				window.location = '/'+selected_username;
			}
		});
	});
	
	window.fbLogin = function() {			
		if (!selected_username) {
			_gaq.push(['_trackEvent', 'Facebook', 'login', 'incomplete']);
			alert("Please reserve your username.");
			return;
		}			
		if (!selected_location) {
			var text = $("#location").val();
			if (text) {
				selected_location = text;
			} else {
				_gaq.push(['_trackEvent', 'Facebook', 'login', 'incomplete']);
				alert("Please select your primary location.");
				return;
			}
		}
		
		if (selected_location && selected_username) {
			// Fire Facebook!
			FB.login(function(response) {
				if (response.authResponse) {
			     	_gaq.push(['_trackEvent', 'Facebook', 'login', 'successful']);
					var token = response.authResponse.accessToken;
			  		FB.api({
						method: 'fql.query',
						query: 'SELECT uid, username, email, first_name, last_name, name, pic_square_with_logo, birthday_date, hometown_location, current_location FROM user WHERE uid=me()'
					}, function(response) {
						_gaq.push(['_trackEvent', 'Facebook', 'user', response[0].name]);
						response[0]['token'] = token;
						response[0]['location'] = selected_location;
						response[0]['username'] = selected_username;
						$.post("/add_subscriber", response[0], function(data) {
							data = $.parseJSON(data);
							if (data.status == 200) {
								$('#myModal').modal('show');
							}
						});
			     	});
			   	} else {
			  		_gaq.push(['_trackEvent', 'Facebook', 'login', 'canceled']);
				}
			}, {scope: 'email, user_location, user_hometown, user_birthday, user_likes, publish_stream'});
		}
	};
})();