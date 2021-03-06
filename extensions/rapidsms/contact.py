from django.db import models
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _, ugettext_lazy as __
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError



class WebContact(models.Model):
    """
        Use the magic extensions feature from rapidsms to inject a 
        a relation to the user in the contact
    """
    
    user = models.ForeignKey(User, blank=True, related_name='contacts')

    class Meta:
        abstract = True
    
    
    def generate_user(self):
        """
            Create automatically a user from the contact, using it's 
            default connection identity as a username of some mix between
            ids and the contact name slug.
        """
        username = slugify(self.name)
        
        while User.objects.filter(username=username).exists():
            try:
                s = username.rsplit('_', 1)
                username = "%s_%s" % (s[0], int(s[1]) + 1)
            except (IndexError, ValueError):
                username = username + "_1" 
                
        return User.objects.create(username=username)


    def save(self, *args, **kwargs):
        
        # autocreate the user
        if not self.user_id:
            self.user = self.generate_user()
            models.Model.save(self, *args, **kwargs)
            
        else:
            # check for duplicate user usage among contacts
            try:
                contact = self.__class__.objects\
                                        .exclude(pk=self.pk)\
                                        .get(user=self.user)
            except self.__class__.DoesNotExist:
                 models.Model.save(self, *args, **kwargs)
            else:
                raise IntegrityError(_(u"The user %(user)s is already "\
                                       u"associated with the contact "\
                                       u"%(contact)s" % {'user': self.user,
                                                         'contact': contact}))
       
        
    def has_role(self, role=None, group=None, context=None):
        """
            Check if this contact has this role. Will try to match either
            role, or a combination of group and context.
            
            Role can be either a role object or a role code.
            
            Group can be either the group name of the group object.
        """
    
        return self.role_set.match(role, group, context).exists()
        
        
    def roles_count(self, group=None, context=None):
        """
            Return how many roles the contact has with this group 
            or this context.
            
            Group can be either the group name of the group object.
        """
    
        if not (bool(group) ^ bool(context)):
            raise ValueError(u'This method expects one and only argument')
        
        return self.role_set.match(group=group, context=context).count()
            
    
    def add_role(self, role=None, group=None, context=None, create=False):
        """
            Adds a role to this contact with this group and this context.
            
            Role can be either a role object or a role code.
            
            Group can be either the group name of the group object.
            
            If the group/role doesn't exists:
                - create == True: create them
                - create == False: raises DoesNotExist
                
            If create is True, returns a tuple with:
                - role: a reference to the added role
                - role_created: a bool which is True if it had to create a role
                - group_created: a bool which is True if it had to create a group
        """
        
        role_mgr = self.role_set.model.objects
        
        if not create:
            return self.role_set.add(role_mgr.get_role(role, group, context)) 
            
        role, role_created, group_created = role_mgr.get_role(role, group, 
                                                               context, create)
        self.role_set.add(role)
        
        return role, role_created, group_created
        

    def remove_role(self, role=None, group=None, context=None):
        """
            Removes a role to this contact with this group and this context.
            
            Role can be either a role object or a role code.
            
            Group can be either the group name of the group object.
            
            If the group/role doesn't exists, raises DoesNotExist
                
        """

        self.role_set.remove(self.role_set.model.objects.get_role(role, 
                                                                  group, 
                                                                  context)) 
       
            
    def is_registered(self):
        """
            Return wether a contact is registered or not.
        """
    
        return self.name and self.connection_set.count()
