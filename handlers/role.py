#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandlerI18n
from rapidsms.models import Contact
from django.utils.translation import ugettext as _
from django.conf import settings


from ..decorators import registration_required
from ..models import Role


class RoleHandler(KeywordHandlerI18n):
    """
        Add a role
    """

    keyword = "role"

    aliases = (
               ('fr', ('role',)),
               )
        
    aliases += getattr(settings, 'RAPIDSMS_ROLE_ALIASES', ())
    
    AUTO_SET_LANG = getattr(settings, 'RAPIDSMS_ROLE_AUTO_SET_LANG',
                             True)

    def help(self, keyword, lang_code):
        self.respond(_(u"To give you a role, send: ROLE <code1> <code2>"))


    @registration_required()
    def handle(self, text, keyword, lang_code):
    
        conn = self.msg.connection
        contact = conn.contact
        
        roles_code = (self.clean_string(code) for code in text.split())
        roles = set()
        roles_with_error = set()
        contact_has_roles = set()
        
        for code in roles_code:
            try:
                role = Role.objects.get(code=code)
            except Role.DoesNotExist:
                roles_with_error.add(code)
            else:
                if contact.has_role(role):
                    contact_has_roles.add(role)
                else:
                    roles.add(role)
                    contact.role_set.add(role)
            
        if roles_with_error:    
            return self.respond(_(u"These roles do not exist: '%(roles)s'. "\
                                  u"Retry after correcting or removing them.") % {
                                   'roles': "', '".join(roles_with_error)})
        
        if roles:                           
            msg = _(u"You are now: '%(roles)s'.")
            
            if contact_has_roles:
                msg += _(u" You already have the other roles.")

            self.respond(msg % {'roles': ", ".join(unicode(r) for r in roles)})
        else:
            self.respond(_(u"You already have these roles."))
