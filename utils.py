#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
    Various helpers and shortcuts
"""


from django.utils.translation import ugettext as _

from handlers_i18n.exceptions import ExitHandle


try:
    from django_simple_config.models import Configuration
except ImportError:
    # it's not install, then you can't close registration
    def are_registrations_closed():
        return 0
else:
    
    if not Configuration.objects.filter(key='close_registrations').exists():
        Configuration.objects.create(key='close_registrations', value='0')
    
    def are_registrations_closed():
        """
            Check if registration are opened or not
        """
        return int(Configuration.get('close_registrations', "0"))
        

def require_registration(message, carry_on=False):
    """
        Exit the handle if the contact is not registered
    """
    contact = message.connection.contact
    if not contact or not contact.is_registered():
        raise ExitHandle(_(u"You must be registered to do this. Send: "\
                           u"REGISTER <first name> <last name>"), carry_on)
                               
                               
def require_role(message, role=None, group=None, context=None, carry_on=False):
    """
        Exit handle if the contact hasn't this role.
    """
    
    require_registration(message, carry_on)
    
    contact = message.connection.contact
        
    role_obj = contact.role_set.model.objects.get_role(role, group, context)
    
    from django.utils import translation
    
    if not contact.has_role(role_obj):
        raise ExitHandle(_(u"You must be %(role)s to do this") % {
                           'role': role_obj}, carry_on)
    
