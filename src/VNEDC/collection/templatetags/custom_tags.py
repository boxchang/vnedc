from django.template import Library
register = Library()


@register.simple_tag
def get_param_value(object, property):
    result = ""
    try:
        result = getattr(object, "T" + property)
    except Exception as e:
        pass

    return result
