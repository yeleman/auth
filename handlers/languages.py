#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandlerI18n
from rapidsms.models import Contact
from django.utils import translation
from django.utils.translation import ugettext as _, activate
from django.conf import settings


from ..decorators import registration_required


class LanguagesHandlerI18n(KeywordHandlerI18n):
    """
    List langs
    """

    keyword = "languages"
    
    aliases = (
                ('en', ('langs', 'languages')),
                ('fr', ('langues', 'langages')),
              )
              
    aliases += getattr(settings, 'RAPIDSMS_LANGUAGES_ALIASES', ())
    
    AUTO_SET_LANG = getattr(settings, 'RAPIDSMS_LANGUAGES_AUTO_SET_LANG', True)


    def help(self, keyword, lang_code):
        return self.handle('', keyword, lang_code)
    

    def handle(self, text, keyword, lang_code):
    
        # todo: fix plural here
        # todo: fix the translation here: it's never translated and I don't
        # know why
        if text:
            return self.respond(_(u"%(keyword)s must be sent with nothing else. "\
                                u"Did you mean %(keyword_sing)s (singular)?") % {
                                'keyword': keyword.upper(), 
                                'keyword_sing': keyword.upper().rstrip('S')})
    
        msg = ''
        contact = Contact.objects.get(pk=self.msg.connection.contact.pk)
        languages = dict(settings.LANGUAGES)
        
        if contact and contact.is_registered():
            msg += _(u"Your prefered language is: '%(language)s'. ") % {
                    'language': _(languages[contact.language])}
    
        msg += _(u"The current language is: '%(language)s'. ") % {
                 'language': _(languages[translation.get_language()])}
    
        msg += _(u"The language for the keyword '%(keyword)s' is: "\
                 u"%(language)s.") % { 'keyword': keyword, 
                 'language': _(languages[lang_code])}
    
        return self.respond(msg)
