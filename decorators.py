"""
    Decorator to check for credential before handling
"""

from django.utils.translation import ugettext as _

def registration_required(carry_on=False) :
    """
        Put it before handle, will check if the user is registered.
        If 'carry_on=False', then the decorator will anwser your need
        a registration, otherwise it will just skip this handler.
    """

    def decorator(func) :

        def wrapper(self, *args, **kwargs) :
            from django.utils import translation
        
            contact = self.msg.connection.contact
            
            if contact and contact.is_registered():
                return func(self, *args, **kwargs)
                
            if carry_on:
                return False
            self.respond(_(u"You must be registered to do this. Send: "\
                           u"REGISTER <first name> <last name>"))
            
            return True

        return wrapper

    return decorator
