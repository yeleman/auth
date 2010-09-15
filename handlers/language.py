#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandlerI18n
from rapidsms.models import Contact
from django.utils.translation import ugettext as _
from django.conf import settings


class LanguageHandlerI18n(KeywordHandlerI18n):
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
                ('en-us', ('lang',)),
                ('fr', ('langue', 'langage')),
              )
              
    aliases += getattr(settings, 'RAPIDSMS_LANGUAGES_ALIASES', ())


    def help(self):
        self.respond(_(u"To set your language, send LANGUAGE <CODE>"))


    def handle(self, text, keyword, lang_code):
    
        print text
        print lang_code
        
        contact = self.msg.connection.contact
        if not contact:
            return self.respond_error(
                _(u"You must JOIN or IDENTIFY yourself before you can "\
                  u"set your language preference."))
             
        t = text.lower().strip()
        for code, name in settings.LANGUAGES:
            if t in (code.lower().strip(), name.lower().strip()):
                contact.language = code
                contact.save()
                return self.respond(_(u"I will speak to you in %(language)s.") % {
                                      'language': _(name)})

        return self.respond_error(_(u'Sorry, I don\'t speak "%(language)s".'),
                                    language=text)
