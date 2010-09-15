#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


from handlers_i18n.handlers.keyword import KeywordHandlerI18n
from rapidsms.models import Contact
from django.utils.translation import ugettext as _
from django.conf import settings


class RegisterHandler(KeywordHandlerI18n):
    """
    Allow remote users to register themselves, by creating a Contact
    object and associating it with their Connection. For example::

        >>> RegisterHandler.test('join Adam Mckaig')
        ['Thank you for registering, Adam Mckaig!']

        >>> Contact.objects.filter(name="Adam Mckaig")
        [<Contact: Adam Mckaig>]
        
    The module will respond according to the language of the keyword::
        
        >>> RegisterHandler.test('inscription Bob')
        ['Merci de vous être enregistré, Bob!']

    Note that the ``name`` field of the Contact model is not constrained
    to be unique, so this handler does not reject duplicate names. If
    you wish to enforce unique usernames or aliases, you must extend
    Contact, disable this handler, and write your own.
    
    If a contact tries to register twice, it's name will be changed if it's
    different of it will reponds that the user it already registered.
    
    You can add aliases for different languages at runtime by setting
    RAPIDSMS_REGISTRATION_ALIASES in your settings.py. 
    
    You can enable or disable settings by setting registration_is_open to 
    True in the database.
    
    """

    keyword = "register"

    aliases = (
               ('en-us', ('reg', 'join',)),
               ('fr', ('inscription', 'rejoindre',)),
               )
        
    aliases += getattr(settings, 'RAPIDSMS_REGISTRATION_ALIASES', ())
    
    AUTO_SET_LANG = getattr(settings, 'RAPIDSMS_REGISTRATION_AUTO_SET_LANG',
                             True)

    def help(self, keyword, lang_code):
        self.respond(_(u"To register, send: JOIN <NAME>"))


    def flatten_name(self, name):
        """
            Return a lowercase name extra spaces.
        """
        return " ".join(name.lower().strip().split())
        

    def handle(self, text, keyword, lang_code):
    
        conn = self.msg.connection
        contact = conn.contact
        
        if contact:
        
            if self.flatten_name(contact.name) == self.flatten_name(text):
                msg =  _(u"You are already registered, %(name)s") % {
                        'name': text}
           
            else:
                msg =  _(u"We changed your name from, '%(old_name)s' to "\
                         u"'%(new_name)s'") % { 'old_name': contact.name, 
                                            'new_name': text }
                contact.name = text
                contact.save()
        else:
    
            conn.contact = Contact.objects.create(name=text, language=lang_code)
            conn.save()
            msg = _(u"Thank you for registering, %(name)s!") % {'name': text}

        self.respond(msg)
