from django import template
register = template.Library()

@register.simple_tag
def custom_url_tag(url):
   proper_url = url.split('/')[0]
   return proper_url

@register.filter(name='to_int')
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0