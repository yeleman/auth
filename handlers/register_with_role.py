#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


from django.utils.translation import ugettext as _
from django.conf import settings

from rapidsms.models import Contact

from handlers_i18n.handlers.callback import CallbackHandler

from ..utils import are_registrations_closed
from ..models import Role


class RegisterWithRoleHandler(CallbackHandler):
    u"""
    Allow remote users to register themselves, like register.py does, and 
    add a role at the same time, like role.py does::

        >>> from django.contrib.sites.models import Site
        >>> from auth.models import Role
        >>> site = Site.objects.get(pk=1)
        >>> role, cr, cg = Role.objects.get_role(group='Webmaster', context=site, create=True)
        >>> RegisterWithRoleHandler.test('r001 Bob')
        ['Bob, you are now registered as: Webmaster of example.com']
        >>> Role.objects.all()[0].group.delete(); Role.objects.all().delete()

    """

    @classmethod
    def match(cls, msg):
        """
            Check if the first keyword is a role.
        """
        
        try:
            text = msg.text.split()
            role_code = text.pop(0).strip().lower()
            return Role.objects.get(code=role_code), ' '.join(text).strip()
        except (IndexError, Role.DoesNotExist):
            return False


    def handle(self, match):
    
        role, name = match
    
        conn = self.msg.connection
        contact = conn.contact
        
        if contact and contact.is_registered():
            msg =  _(u"You are already registered, %(name)s. To change "\
                     u"your name, send: REGISTER") % {'name': name}
        else:
            if not are_registrations_closed():
                conn.contact = Contact.objects.create(name=name)
                conn.save()
                conn.contact.role_set.add(role)
                
                msg = _(u"%(name)s, you are now registered as: %(role)s") % { 
                        'role': role, 'name': name}
            else:
                msg = _(u"Registration are closed. Ask your administrator for "\
                        u"more informations")
            
        self.respond(msg)
