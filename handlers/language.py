#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandler
from rapidsms.models import Contact
from django.utils import translation
from django.utils.translation import ugettext as _, activate
from django.conf import settings


from ..decorators import registration_required


class LanguageHandler(KeywordHandler):
    """
    Allow remote users to set their preferred language, by updating the
    ``language`` field of the Contact associated with their connection.
    
    Allow i18n for keywords.
    
    You should must ensure your LANGUAGES setting match the aliases here 
    otherwise translations may be inconsistent.
    
    You can add aliases for different languages at runtime by setting
    RAPIDSMS_LANGUAGES_ALIASES in your settings.py. 
    """

    keyword = "language"
    
    aliases = (
                ('en', ('lang', 'language')),
                ('fr', ('langue', 'langage')),
              )
              
    aliases += getattr(settings, 'RAPIDSMS_LANGUAGE_ALIASES', ())
    
    AUTO_SET_LANG = getattr(settings, 'RAPIDSMS_LANGUAGE_AUTO_SET_LANG', True)

    def help(self, keyword, lang_code):
        return self.respond(_(u"To choose you language, send: LANGUAGE "\
                              u"<language name>"))


    @registration_required()
    def handle(self, text, keyword, lang_code):
    
        contact = self.msg.connection.contact
           
        t = text.lower().strip()
        for code, name in settings.LANGUAGES:
            if t in (code.lower().strip(), name.lower().strip()):
                Contact.objects.filter(pk=contact.pk).update(language=code)
                contact.language = code
                activate(code)
                
                return self.respond(_(u"I will speak to you in %(language)s.") % {
                                      'language': _(name)})

        # todo: this doesn't work with unicode because of a bug in outgoing.py
        # (it uses gettext instead of ugettext)
        return self.respond_error(_(u'Sorry, I don\'t speak "%(language)s".') % {
                                    'language': _(text)})
