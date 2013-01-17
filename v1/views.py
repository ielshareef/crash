from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson
from prelaunch.models import Earlybird
from django.utils import timezone
import datetime
import time
import re
import mailchimp
from mailchimp.chimpy.chimpy import ChimpyException
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import facebook
import requests
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache


# list of mobile User Agents
mobile_uas = [
	'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
	'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
	'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
	'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
	'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
	'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
	'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
	'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
	'wapr','webc','winw','winw','xda','xda-'
	]
 
mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone' ]

reserved_usernames = ['search', '404', 'company', 'bill', 'cities', 'locations', 'destinations', 'leaderboard', 'attraction', 'photo']

def mobileBrowser(request):
	''' Super simple device detection, returns True for mobile devices '''
	
	mobile_browser = False
	ua = request.META['HTTP_USER_AGENT'].lower()[0:4]
	
	if (ua in mobile_uas):
		mobile_browser = True
	else:
		for hint in mobile_ua_hints:
			if request.META['HTTP_USER_AGENT'].find(hint) > 0:
				mobile_browser = True
	
	return mobile_browser

@ensure_csrf_cookie
@cache_page(60 * 60 * 24 * 30)
def index(request):
	token = api_token(request)
	u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
	if u:
		graph = facebook.GraphAPI(u["access_token"])
		profile = graph.get_object("me")
		if mobileBrowser(request):
			return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:	
		if mobileBrowser(request):
			return render_to_response('index.html', {'token': token, 'req': request})
		else:
			return render_to_response('index.html', {'token': token, 'req': request})

@ensure_csrf_cookie
@never_cache
def profile(request, un):
	try:
		token = api_token(request)
		content = {'access_token': token, 'username': un, 'summary': '0'}
		r = requests.get("http://crash-api.herokuapp.com/1.0/users.json", params=content)
		if r.status_code != requests.codes.ok:
			token = api_token(request, True)
			res = HttpResponseRedirect(request.build_absolute_uri())
			res.delete_cookie('api_token')
			return res
			
		if not r.json:
			raise Http404
			
		content = {'access_token': token, 'user_id': r.json[0]['id'], 'summary': '0', 'count': '21', 'type': 'photo'}
		ck = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
		if ck.status_code != requests.codes.ok:
			ck.raise_for_status()
			
		content = {'access_token': token, 'user_id': r.json[0]['id'], 'count': '25'}
		follows = requests.get("http://crash-api.herokuapp.com/1.0/follows.json", params=content)
		if follows.status_code != requests.codes.ok:
			follows.raise_for_status()
			
		content = {'access_token': token, 'user_id': r.json[0]['id'], 'count': '25'}
		followers = requests.get("http://crash-api.herokuapp.com/1.0/followers.json", params=content)
		if followers.status_code != requests.codes.ok:
			followers.raise_for_status()
			
		u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
		user_name = r.json[0]['username']
				
		if len(ck.json):
			main_checkin = ck.json.pop(0)
		else:
			main_checkin = []
			
		if mobileBrowser(request):
			return render_to_response('profile.html', {'user': r.json[0], 'follows': follows.json, 'followers': followers.json, 'user_name': user_name, 'main_checkin': main_checkin, 'checkins': ck.json[1::], 'location': r.json[0]['preferred_region']['name'].split(', ')[0], 'token': token, 'req': request })
		else:
			return render_to_response('profile.html', {'user': r.json[0], 'follows': follows.json, 'followers': followers.json, 'user_name': user_name, 'main_checkin': main_checkin, 'checkins': ck.json[1::], 'location': r.json[0]['preferred_region']['name'].split(', ')[0], 'token': token, 'req': request })
		
	except ObjectDoesNotExist:
		raise Http404
		
def profile_discovered(request, un):
	try:
		token = api_token(request)
		user = Earlybird.objects.get(username__iexact=un)
		dt = user.join_date.strftime('%b %d, %Y')
		u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
		if u:
			if mobileBrowser(request):
				return render_to_response('profile_discovered.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0], 'req': request })
			else:
				return render_to_response('profile_discovered.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0], 'req': request })
		else:
			if mobileBrowser(request):
				return render_to_response('profile_discovered.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0], 'req': request })
			else:
				return render_to_response('profile_discovered.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0], 'req': request })
	except ObjectDoesNotExist:
		raise Http404
		
def profile_friends(request, un):
	try:
		token = api_token(request)
		user = Earlybird.objects.get(username__iexact=un)
		dt = user.join_date.strftime('%b %d, %Y')
		u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
		if u:
			if mobileBrowser(request):
				return render_to_response('profile_friends.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
			else:
				return render_to_response('profile_friends.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
		else:
			if mobileBrowser(request):
				return render_to_response('profile_friends.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
			else:
				return render_to_response('profile_friends.html', {'lname': user.first_name, 'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
	except ObjectDoesNotExist:
		raise Http404

@ensure_csrf_cookie
@never_cache
def profile_city(request, city):
	token = api_token(request)
	content = {'access_token': token}
	r = requests.get("http://crash-api.herokuapp.com/1.0/regions/"+city+".json", params=content)
	if r.status_code != requests.codes.ok:
		token = api_token(request, True)
		res = HttpResponseRedirect(request.build_absolute_uri())
		res.delete_cookie('api_token')
		return res
	
	if not r.json:
		raise Http404
			
	content = {'access_token': token, 'region_id': r.json['id'], 'count': '100', 'summary': '0', 'ORDER': 'DESC'}
	atr = requests.get("http://crash-api.herokuapp.com/1.0/attractions.json", params=content)
	if atr.status_code != requests.codes.ok:
		atr.raise_for_status()
		
	if mobileBrowser(request):
		return render_to_response('profile_city.html', {'details': r.json, 'checkins': atr.json[0:20], 'attr': atr.json, 'city': r.json['name'], 'settled': r.json['settled'], 'desc': r.json['description'], 'token': token, 'req': request})
	else:
		return render_to_response('profile_city.html', {'details': r.json, 'checkins': atr.json[0:20], 'attr': atr.json, 'city': r.json['name'], 'settled': r.json['settled'], 'desc': r.json['description'], 'token': token, 'req': request})

@ensure_csrf_cookie
@never_cache		
def attraction(request, attraction):
	token = api_token(request)
	content = {'access_token': token}
	r = requests.get("http://crash-api.herokuapp.com/1.0/attractions/"+attraction+".json", params=content)
	if r.status_code != requests.codes.ok:
		token = api_token(request, True)
		res = HttpResponseRedirect(request.build_absolute_uri())
		res.delete_cookie('api_token')
		return res
	
	if not r.json:
		raise Http404
	
	content = {'access_token': token, 'attraction_id': attraction, 'type': 'photo'}
	ck = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if ck.status_code != requests.codes.ok:
		ck.raise_for_status()
	
	ck2 = []	
	for i in ck.json:
		if (i['type'] == 'photo'):
			ck2.append(i)
		
	content = {'access_token': token, 'region_id': r.json['region']['id'], 'count': '100', 'latitude': r.json['latitude'], 'longitude': r.json['longitude']}
	atr = requests.get("http://crash-api.herokuapp.com/1.0/attractions.json", params=content)
	if atr.status_code != requests.codes.ok:
		atr.raise_for_status()
	
	if mobileBrowser(request):
		return render_to_response('attraction.html', {'attraction': r.json, 'checkins': ck2, 'attr': atr.json[1::], 'token': token, 'req': request})
	else:
		return render_to_response('attraction.html', {'attraction': r.json, 'checkins': ck2, 'attr': atr.json[1::], 'token': token, 'req': request})

@ensure_csrf_cookie
@never_cache
def checkin(request, checkin):
	token = api_token(request)
	
	content = {'access_token': token, 'type': 'photo'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins/"+checkin+".json", params=content)
	if r.status_code != requests.codes.ok:
		token = api_token(request, True)
		res = HttpResponseRedirect(request.build_absolute_uri())
		res.delete_cookie('api_token')
		return res

	if not r.json:
		raise Http404
		
	content = {'access_token': token, 'email': r.json['user']['email'], 'summary': '0'}
	ck = requests.get("http://crash-api.herokuapp.com/1.0/users.json", params=content)
	if ck.status_code != requests.codes.ok:
		ck.raise_for_status()
		
	content = {'access_token': token}
	atr = requests.get("http://crash-api.herokuapp.com/1.0/attractions/"+r.json['attraction']['id']+".json", params=content)
	if atr.status_code != requests.codes.ok:
		atr.raise_for_status()
	
	currentUrl = request.get_full_path()
	
	user_name = ck.json[0]['username']
	
	if mobileBrowser(request):
		return render_to_response('checkin.html', {'checkin': r.json, 'attraction': atr.json, 'user_name': user_name, 'user': ck.json[0], 'thisurl': currentUrl, 'token': token, 'req': request})
	else:
		return render_to_response('checkin.html', {'checkin': r.json, 'attraction': atr.json, 'user_name': user_name, 'user': ck.json[0], 'thisurl': currentUrl, 'token': token, 'req': request})
				
def search(request, keyword):
	if mobileBrowser(request):
		return render_to_response('search.html', {'keyword': keyword})
	else:
		return render_to_response('search.html', {'keyword': keyword})

@ensure_csrf_cookie
@cache_page(60 * 60 * 24 * 30)		
def generic(request, pg):
	if mobileBrowser(request):
		return render_to_response(''+ pg +'.html', {'req': request})
	else:
		return render_to_response(pg +'.html', {'req': request})

def get_username(request):
	message = 'void';
	if request.is_ajax():
		if request.method == 'GET':
	  		message = 'does_not_exist';
		elif request.method == 'POST':
			if 'email' in request.POST.keys():
				token = api_token(request)
				content = {'access_token': token, 'email': request.POST['email']}
				r = requests.get("http://crash-api.herokuapp.com/1.0/users.json", params=content)
				if r.status_code != requests.codes.ok:
					r.raise_for_status()

				if r.json:
					message = r.json[0]['username']
				else:
					message = 'does_not_exist';
			else:
				message = 'does_not_exist';
		else:
			message = 'does_not_exist';
	return HttpResponse(message);
						
def api_token(req, skip_cookie=False):
	# No token is found
	if skip_cookie or 'api_token' not in req.COOKIES.keys():
		# Is this an authenticated user?
		if 'user_username' in req.COOKIES.keys():
			passwd = (int(req.COOKIES['user_uid'][0:4]) + 1341) * 1341
			content = {'username': req.COOKIES['user_username'], 'password': passwd, 'client_id': '21_2rqrzy46qfi8g0w8gk4o8ccwc48c84sskogoocgswkwko8gkgs', 'client_secret': '6yh193q42dc00og0s8w4080c0ggwkgckg4cgggk440008ksk8', 'grant_type': 'password', 'response_type': 'token'}
			r = requests.get("http://crash-api.herokuapp.com/oauth/v2/token", params=content)
			if r.status_code == requests.codes.ok:
				return r.json['access_token']
			else:
				return guest_token()
		else:
			# Not a user
			return guest_token()
	else:
		#Token is found
		return req.COOKIES['api_token']
		
def guest_token():
	content = {'client_id': '11_1w0sopvk6ge8s44w0w88gsssco0k8og8cgwwcoo8gc0o80wo4g', 'client_secret': '38rh8fjtfqo044k80ccg8g4ws40s0kgogccgsgkog48ok8sgw', 'grant_type': 'client_credentials'}
	r = requests.get("http://crash-api.herokuapp.com/oauth/v2/token", params=content)
	if r.status_code == requests.codes.ok:
		return r.json['access_token']
	else:
		return r.raise_for_status()
		
def add_like(request):
	if 'checkin' in request.POST.keys():
		token = api_token(request)
		content = {'access_token': token, 'checkin_id': request.POST['checkin']}
		r = requests.post("http://crash-api.herokuapp.com/1.0/likes.json", params=content)
		if r.status_code != requests.codes.ok:
			message = 'NOT OK'
		else:
			message = 'OK'
		
	return HttpResponse(simplejson.dumps(message));
	
def delete_like(request):
	if 'checkin' in request.POST.keys():
		token = api_token(request)
		content = {'access_token': token, 'checkin_id': request.POST['checkin']}
		r = requests.delete("http://crash-api.herokuapp.com/1.0/likes.json", params=content)
		if r.status_code != requests.codes.ok:
			message = 'NOT OK'
		else:
			message = 'OK'

	return HttpResponse(simplejson.dumps(message));
	
def load_more(request):
	if 'user_id' in request.POST.keys() and 'before_id' in request.POST.keys():
		token = api_token(request)
		content = {'access_token': token, 'before_id': request.POST['before_id'], 'user_id': request.POST['user_id'], 'summary': '0', 'count': '20', 'type': 'photo'}
		ck = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
		if ck.status_code != requests.codes.ok:
			message = {'error': ck.status_code }
		else:
			message = ck.json

	else:
		message = {'error': 'Right pramaters were not passed' }
	return HttpResponse(simplejson.dumps(message));
	
def load_more_in_region(request):
	if 'region_id' in request.POST.keys() and 'before_id' in request.POST.keys():
		token = api_token(request)
		content = {'access_token': token, 'after_id': request.POST['before_id'], 'order': 'DESC', 'count': '20', 'summary': '0', 'region_id': request.POST['region_id']}
		ck = requests.get("http://crash-api.herokuapp.com/1.0/attractions.json", params=content)
		if ck.status_code != requests.codes.ok:
			message = {'error': ck.status_code }
		else:
			message = ck.json
		
	else:
		message = {'error': 'Right pramaters were not passed' }
		
	return HttpResponse(simplejson.dumps(message));
	
def contact_us(request):
	if 'name' in request.POST.keys() and 'email' in request.POST.keys():
		send_mail('Crash Contact: '+request.POST['subject'], 'Name: ' + request.POST['name'] + '\nEmail: '+request.POST['email']+'\nSubject: '+request.POST['subject']+'\n\nMessage: '+request.POST['message'], 'noreply@crashla.com', ['ielshareef@gmail.com', 'feedback@crashla.com'], fail_silently=False)
		message = {'message': 'OK' }
		
	else:
		message = {'error': 'Right pramaters were not passed' }

	return HttpResponse(simplejson.dumps(message));

@ensure_csrf_cookie
@cache_page(60 * 60 * 24 * 30)	
def about_us_team(request):
	token = api_token(request)
	res = []
	total_attr = 0
	total_chk = 0
	total_ph = 0
	
	#Get LA stats
	content = {'access_token': token}
	r = requests.get("http://crash-api.herokuapp.com/1.0/regions/11.json", params=content)
	if r.status_code != requests.codes.ok:
		token = api_token(request, True)
		res = HttpResponseRedirect(request.build_absolute_uri())
		res.delete_cookie('api_token')
		return res
		
	total_attr += int(r.json['attractions'])
	total_chk += int(r.json['total_checkins'])
	total_ph += int(r.json['total_photos'])
	
	#Get SF stats
	content = {'access_token': token}
	r = requests.get("http://crash-api.herokuapp.com/1.0/regions/441.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	total_attr += int(r.json['attractions'])
	total_chk += int(r.json['total_checkins'])
	total_ph += int(r.json['total_photos'])
	
	#Get SD stats
	content = {'access_token': token}
	r = requests.get("http://crash-api.herokuapp.com/1.0/regions/511.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	total_attr += int(r.json['attractions'])
	total_chk += int(r.json['total_checkins'])
	total_ph += int(r.json['total_photos'])
	
	#Get Erick Laubach
	content = {'access_token': token, 'user_id': '121', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
		
	#Get Tim Laubach
	content = {'access_token': token, 'user_id': '381', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
		
	# Get Ismail Laubach
	content = {'access_token': token, 'user_id': '101', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
			
	res.append(r.json)
	
	# Get Scott Laubach
	content = {'access_token': token, 'user_id': '51', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Maya Laubach
	content = {'access_token': token, 'user_id': '511', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Lisa Laubach
	content = {'access_token': token, 'user_id': '91', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Selena Laubach
	content = {'access_token': token, 'user_id': '81', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Steve Laubach
	content = {'access_token': token, 'user_id': '131', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Ed Laubach
	content = {'access_token': token, 'user_id': '1331', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
		
	res.append(r.json)
	
	# Get Andrew Laubach
	content = {'access_token': token, 'user_id': '4821', 'count': '6', 'type': 'photo', 'order': 'DESC'}
	r = requests.get("http://crash-api.herokuapp.com/1.0/checkins.json", params=content)
	if r.status_code != requests.codes.ok:
		r.raise_for_status()
										
	res.append(r.json)
	
	return render_to_response('about_us.html', {'team': res, 'total_attr': total_attr, 'total_chk': total_chk, 'total_ph': total_ph, 'token': token, 'req': request})
