from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from prelaunch.models import Earlybird
from django.utils import timezone
import datetime
import time
import mailchimp
from mailchimp.chimpy.chimpy import ChimpyException
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import facebook

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

reserved_usernames = ['search', '404', 'company', 'bill', 'cities', 'locations', 'destinations', 'leaderboard', 'attraction']

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

def index(request):
	u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
	if u:
		graph = facebook.GraphAPI(u["access_token"])
		profile = graph.get_object("me")
		user = Earlybird.objects.get(id=profile['id'])
		if mobileBrowser(request):
			return HttpResponseRedirect('/'+user.username)
		else:
			return HttpResponseRedirect('/'+user.username)
	else:	
		if mobileBrowser(request):
			return render_to_response('mobile/index2.html')
		else:
			return render_to_response('index2.html')
	
def profile(request, un):
	try:
		user = Earlybird.objects.get(username__iexact=un)
		dt = user.join_date.strftime('%b %d, %Y')
		u = facebook.get_user_from_cookie(request.COOKIES, '100928086720891', '1e2dbf3c69829df5e765b548fd489850')
		if u:
			if mobileBrowser(request):
				return render_to_response('mobile/profile2.html', {'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
			else:
				return render_to_response('profile2.html', {'name': user.first_name + ' ' + user.last_name, 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
		else:
			if mobileBrowser(request):
				return render_to_response('mobile/profile2.html', {'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
			else:
				return render_to_response('profile2.html', {'name': user.first_name + ' ' + user.last_name[0:1], 'photo': user.photo, 'date': dt, 'username': un, 'location': user.primary_location.split(', ')[0] })
	except ObjectDoesNotExist:
		return render_to_response('index2.html')
		
def get_username(request):
	message = 'void';
	if request.is_ajax():
		if request.method == 'GET':
	  		message = 'void';
		elif request.method == 'POST':
			# Check the db
			p = Earlybird.objects.get(id=request.POST['uid'])
			if not p:
				message = 'void';
			else:
				message = p.username
		else:
			message = 'void';
	return HttpResponse(message);
	
	
def check_username(request):
	message = {'error': 100, 'message': "This is not an AJAX request. Sorry, we can't help you."}
	if request.is_ajax():
		if request.method == 'GET':
	  		message = {'error': 200, 'message': "This is a GET AJAX request. We're expecting a user object POSTed to us."}
		elif request.method == 'POST':
			# Is the name reserved?
			if (request.POST['username'].lower() in reserved_usernames):
				message = {'error': 300, 'message': "Username is taken. Sorry."}
			else:
				# Check the db
				p = Earlybird.objects.filter(username__iexact=request.POST['username'])
				if not p:
					# Username is available!
					message = {'status': 200, 'message': "All good."}
				else:
					# Username is taken :/
					message = {'error': 300, 'message': "Username is taken. Sorry."}
		else:
			message = {'error': 100, 'message': "This looks like an AJAX request but it's not. Sorry, we can't help you."}
	return HttpResponse(simplejson.dumps(message));
		
def add_subscriber(request):
	message = {'error': 100, 'message': "This is not an AJAX request. Sorry, we can't help you."}
	if request.is_ajax():
		if request.method == 'GET':
	  		message = {'error': 200, 'message': "This is a GET AJAX request. We're expecting a user object POSTed to us."}
		elif request.method == 'POST':
			# format the birthday
			b = datetime.datetime.strptime(request.REQUEST['birthday_date'], "%m/%d/%Y")
			birthdate = b.strftime('%Y-%m-%d')
			
			# check values
			fb_loc = request.POST['current_location[name]'] if 'current_location[name]' in request.POST.keys() else 'N/A'
			fb_home = request.POST['hometown_location[name]'] if 'hometown_location[name]' in request.POST.keys() else 'N/A'
			
			# Get a bigger pic
			pic = request.POST['pic_square_with_logo'].replace('q.', 'o.')
			# Setup the query for adding a new subscriber!
			p = Earlybird(id=request.POST['uid'], \
			first_name=request.POST['first_name'], \
			last_name=request.POST['last_name'], \
			birthday=birthdate, \
			email=request.POST['email'], \
			location=fb_loc, \
			primary_location=request.POST['location'], \
			hometown=fb_home, \
			username=request.POST['username'], \
			photo_sq=request.POST['pic_square_with_logo'], \
			photo=pic, \
			facebook_token=request.POST['token'], \
			join_date=timezone.now())
			p.save()
			send_mail(request.POST['location'], 'Name: ' + request.POST['first_name'] + ' ' + request.POST['last_name'] + '\nUsername: '+request.POST['username']+'\nPrimary City: '+request.POST['location']+'\n\nEmail: '+request.POST['email']+'\nCurrent Location: '+fb_loc+'\nHometown: '+fb_home, 'noreply@crashla.com',
			    ['ielshareef@gmail.com', 'crash@cottonblend.com'], fail_silently=False)
			try:
				list = mailchimp.utils.get_connection().get_list_by_id('57648fc033')
				list.subscribe(request.POST['email'],{'EMAIL':request.POST['email'], 'FNAME':request.POST['first_name'], 'LNAME':request.POST['last_name'], 'LOC':request.POST['location'], 'HOME': fb_home}, 'html')
			except ChimpyException:
				pass
			message = {'status': 200, 'message': "All good."}
		else:
			message = {'error': 100, 'message': "This looks like an AJAX request but it's not. Sorry, we can't help you."}