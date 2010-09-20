"""
    Decorator to check for credential before handling
"""

from functools import update_wrapper

from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from .models import Role

def registration_required(carry_on=False):
    """
        Put it before handle, will check if the user is registered.
        If 'carry_on=False', then the decorator will anwser your need
        a registration, otherwise it will just skip this handler.
    """

    def decorator(func):
    
        def wrapper(self, *args, **kwargs):

            contact = self.msg.connection.contact
            
            if contact and contact.is_registered():
                return func(self, *args, **kwargs)
                
            if carry_on:
                return False
                
            return self.respond(_(u"You must be registered to do this. Send: "\
                           u"REGISTER <first name> <last name>"))
    
        return update_wrapper(wrapper, func)

    return decorator
    

    
def role_required(role=None, group=None, context=None, carry_on=False) :
    """
        Put it before handle, will check if the user has a group.
        If 'carry_on=False', then the decorator will anwser your need
        a this group, otherwise it will just skip this handler.
    """
    
    def decorator(func) :

        def wrapper(self, *args, **kwargs) :
        
            roles = Role.objects.all()

            if role:
                role_obj = roles.get(code=getattr(role, 'code', role))
            else:
                if not (group and context):
                    raise ValueError(u'This decorator expects role '\
                                     u'or group AND context')
                
                ctype = ContentType.objects.get_for_model(context)
                role_obj = roles.get(group__name=getattr(group, 'name', group),
                                 context_type=ctype, 
                                 context_id=context.id)
                    
            contact = self.msg.connection.contact
            
            if not contact or not contact.is_registered():
                return self.respond(_(u"You must be registered to do this. Send: "\
                           u"REGISTER <first name> <last name>"))
               
            if contact.has_role(role_obj):
                return func(self, *args, **kwargs)
            
            else:
                if carry_on:
                    return False
                    
                return self.respond(_(u"You must be %(role)s to do this") % {
                                      'role': role_obj})
            
        return update_wrapper(wrapper, func)

    return decorator
