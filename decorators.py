#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


"""
    Decorator to check for credential before handling
"""

from functools import update_wrapper

from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from .models import Role

from utils import require_registration, require_role


def registration_required(carry_on=False):
    """
        Put it before handle, will check if the user is registered.
        If 'carry_on=False', then the decorator will anwser your need
        a registration, otherwise it will just skip this handler.
    """

    def decorator(func):
    
        def wrapper(self, *args, **kwargs):
        
            require_registration(self.msg, carry_on)

            return func(self, *args, **kwargs)
    
        return update_wrapper(wrapper, func)

    return decorator
    

    
def role_required(role=None, group=None, context=None, carry_on=False) :
    """
        Put it before handle, will check if the user has a group.
        If 'carry_on=False', then the decorator will anwser your need
        a this group, otherwise it will just skip this handler.
    """
    
    def decorator(func) :

        def wrapper(self, *args, **kwargs) :
        
            require_role(self.msg, role, group, context, carry_on)
            
            return func(self, *args, **kwargs)
            
        return update_wrapper(wrapper, func)

    return decorator
