from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'crash.views.home', name='home'),
    # url(r'^crash/', include('crash.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
	(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
	(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
	url(r'^region\/\w+\/(\w+)', 'v1.views.profile_city'),
	url(r'^attraction\/(\d+)\/\w+', 'v1.views.attraction'),
	url(r'^photo\/(\d+)\/\w+', 'v1.views.checkin'),
	url(r'^(privacy_policy)', 'v1.views.generic'),
	url(r'^(terms_of_use)', 'v1.views.generic'),
	url(r'^about_us', 'v1.views.about_us_team'),
	url(r'^search\/(\w+)', 'v1.views.search'),
	url(r'^get_username', 'v1.views.get_username'),
	url(r'^add_like', 'v1.views.add_like'),
	url(r'^delete_like', 'v1.views.delete_like'),
	url(r'^load_more_in_region', 'v1.views.load_more_in_region'),
	url(r'^load_more', 'v1.views.load_more'),
	url(r'^contact_us', 'v1.views.contact_us'),
	url(r'^(\w+)\/discovered', 'v1.views.profile_discovered'),
	url(r'^(\w+)\/friends', 'v1.views.profile_friends'),
	url(r'^(\w+)', 'v1.views.profile'),
	url(r'^', 'v1.views.index'),
	# Prelaunch URLs
	#url(r'^(\w+)', 'prelaunch.views.profile'),
	#url(r'^', 'prelaunch.views.index'),
)
