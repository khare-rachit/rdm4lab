# custom template tags for use in templates
from django import template
from datetime import timedelta
import datetime

register = template.Library()


@register.filter(name="add_str")
def add_str(str1, str2):
    """concatenate str1 & str2"""
    return str(str1) + str(str2)


@register.filter(name="dict_key")
def dict_key(d, k):
    """Returns the given key from a dictionary."""
    return d.get(k)


@register.filter(name="zip_longest")
def zip_longest(list1, list2):
    """Zip two lists together with padding for unequal lengths."""
    max_len = max(len(list1), len(list2))
    return zip(
        list1 + [None] * (max_len - len(list1)), list2 + [None] * (max_len - len(list2))
    )


@register.filter(name="zip")
def zip(list1, list2):
    """Zip two lists together and return a list of tuples."""
    print(list1, list2)
    return zip(list1, list2)


@register.filter(name="get_at_index")
def get_at_index(list, index):
    try:
        return list[index]
    except:
        return None
