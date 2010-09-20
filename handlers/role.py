#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandlerI18n
from rapidsms.models import Contact
from django.utils.translation import ugettext as _
from django.conf import settings


from ..decorators import registration_required


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
        

        self.respond("test")
