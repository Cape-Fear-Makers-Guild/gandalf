from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from datetime import datetime, timedelta

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name="isNetAdmin")
def isNetAdmin(user):
    return user.groups.filter(name=settings.NETADMIN_USER_GROUP).exists()
