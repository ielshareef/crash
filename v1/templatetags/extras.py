from datetime import datetime, timedelta
from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def get_range(value):
	"""
	Filter - returns a list containing range made from given value
	Usage (in template):
	
	<ul>{% for i in 3|get_range %}
	  <li>{{ i }}. Do something</li>
	{% endfor %}</ul>
	
	Results with the HTML:
	<ul>
	  <li>0. Do something</li>
	  <li>1. Do something</li>
	  <li>2. Do something</li>
	</ul>
	
	Instead of 3 one may use the variable set in the views
	"""
	return range( value )

@register.filter
def substr(value,arg):
	return value.lower() in arg.lower()
	
@register.filter
def modulo(value,arg):
	remainder = int(value) % int(arg)
	return int(arg) - remainder

@register.filter
def timesince_threshold(value, days=7):
	"""
	return timesince(<value>) if value is more than <days> old. Return value otherwise
	"""
    
	val = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
	dif = datetime.now() - val
	
	if dif < timedelta(days=days):
		return timesince(val)
	else:
		return dif
		
@register.filter
def split(value, arg):
	return value.__str__().split(arg)[0]
		
timesince_threshold.is_safe = False