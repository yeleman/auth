from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType

from rapidsms.models import Contact, Connection, Backend

from ..models import Role


class RoleBasesAdvanced(TestCase):

            
    def setUp(self):
        
        self.user = User.objects.create(username='Joe')
        self.contact = Contact.objects.create(name='Bob', user=self.user)
        self.backend = Backend.objects.get_or_create(name='message_tester')[0]
        self.connection = Connection(identity='1234', backend=self.backend)
        self.contact.connection_set.add(self.connection)
        self.site = Site.objects.create(domain="www.superwebsite.org")
        self.group = Group.objects.create(name="Webmaster")
        self.role = Role.objects.create(context=self.site, group=self.group)
        self.contact.role_set.add(self.role)
        self.contact.save()
  
  
    def test_is_registered(self):
        
        self.assertTrue(self.contact.is_registered())
        contact = Contact.objects.create(name='Steve')
        self.assertFalse(contact.is_registered())
        
    # todo : 
    # decorator with @require_role(role, group, context), @require_credential(roles=[], groups[], permission=[]), @require_one_credential(roles=[], groups[], permission=[])
    #   
    #@require_registration
     # register role
     # unregister role
     # unregister
    # merge role and register
    
    # todo: @forbidden_to_role, @forbidden_to_group
    

    
