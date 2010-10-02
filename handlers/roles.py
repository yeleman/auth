#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandler
from django.utils.translation import ugettext as _
from django.conf import settings


from ..decorators import registration_required


class RolesHandler(KeywordHandler):
    """
        List roles
    """

    keyword = "roles"

    aliases = (
               ('fr', ('roles',)),
               )
        
    aliases += getattr(settings, 'RAPIDSMS_ROLES_ALIASES', ())
    
    AUTO_SET_LANG = getattr(settings, 'RAPIDSMS_ROLES_AUTO_SET_LANG',
                             True)

    def help(self, keyword, lang_code):
        return self.handle('', keyword, lang_code)


    @registration_required()
    def handle(self, text, keyword, lang_code):
    
        if text:
            return self.respond(_(u"ROLES must be sent with nothing else. Did "\
                                u"you mean ROLE (singular)?"))
    
        contact = self.msg.connection.contact
        
        if contact.role_set.exists():
            return self.respond(_(u"You are: '%(roles)s'. ") % {
              'roles': "', '".join(unicode(r) for r in contact.role_set.all())})
        else:
            return self.respond(_(u"You don't have any role yet. Send: "\
                                  u"'ROLE <code>' to add one."))
        
