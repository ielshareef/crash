from django.db import models

class Earlybird(models.Model):
	id = models.BigIntegerField(primary_key=True)
	username = models.CharField(max_length=20, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(max_length=100)
	location = models.CharField(max_length=200)
	primary_location = models.CharField(max_length=200)
	hometown = models.CharField(max_length=200)
	birthday = models.DateField()
	photo_sq = models.URLField(null=True)
	photo = models.URLField(null=True)
	facebook_token = models.CharField(max_length=255)
	join_date = models.DateTimeField('date published')
	def __unicode__(self):
		return '%s %s' % (self.first_name, self.last_name)