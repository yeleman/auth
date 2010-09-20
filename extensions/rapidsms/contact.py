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
    
        try:
            username = self.default_connection.identity
        except AttributeError:
            username = slugify(self.name)
            if User.objects.filter(username=username).exists():
                username = "%s_%s" % ('ID', slugify(self.name)) 
        else:
            if User.objects.filter(username=username).exists():
                username = "%s_%s" % (username, slugify(self.name),) 
        return User.objects.create(username=username)


    def save(self, *args, **kwargs):
        
        # autocreate the user
        if not self.user_id:
            self.user = self.generate_user()
            models.Model.save(self, *args, **kwargs)
            
            # if the username starts with id, then it means we have to avoir
            # duplicates by replacing it with the contact id
            username = self.user.username
            if username.startswith('ID_'):
                self.user.username = username.replace('ID', str(self.id), 1)
                models.Model.save(self)
                
            return

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
    
        roles = self.role_set.all()
        
        if role:
            return roles.filter(code=getattr(role, 'code', role)).exists()
        else:
            if not (group or context):
                raise ValueError(u'This method expects at least one argument')
            
            if group:
                roles = roles.filter(group__name=getattr(group, 'name', group))
            
            if context:
                ctype = ContentType.objects.get_for_model(context)
                roles = roles.filter(context_type=ctype, context_id=context.id)
            
        return roles.exists()
        
        
    def roles_count(self, group=None, context=None):
        """
            Return how many roles the contact has with this group 
            or this context.
            
            Group can be either the group name of the group object.
        """
    
        if not (bool(group) ^ bool(context)):
            raise ValueError(u'This method expects one and only argument')
        
        if group:
            group_name = getattr(group, 'name', group)
            return self.role_set.filter(group__name=group_name).count()
        
        if context:
            ctype = ContentType.objects.get_for_model(context)
            return self.role_set.filter(context_type=ctype, 
                                     context_id=context.id).count()
            
    
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
        
        if role:
            self.role_set.add(role_mgr.get(code=getattr(role, 'code', role)))
            
        else:
            if not (group or context):
                raise ValueError(u'You must provide a role or a group '\
                                 u'AND a context')
        
            gr_name = getattr(group, 'name', group)
            ctype = ContentType.objects.get_for_model(context)
        
            if not create:
                group = Group.objects.get(name=gr_name)
                role = role_mgr.get(group=group, context_type=ctype, 
                                                 context_id=context.id)
                self.role_set.add(role) 
            
            else:   
                group, group_created = Group.objects.get_or_create(name=gr_name)
                
                role, role_created = role_mgr.get_or_create(group=group,
                                                            context_type=ctype, 
                                                          context_id=context.id)
            
                self.role_set.add(role) 
                                                                   
                return role, role_created, group_created
        

    def remove_role(self, role=None, group=None, context=None):
        """
            Removes a role to this contact with this group and this context.
            
            Role can be either a role object or a role code.
            
            Group can be either the group name of the group object.
            
            If the group/role doesn't exists, raises DoesNotExist
                
        """
        
        role_mgr = self.role_set.model.objects
        
        if role:
            self.role_set.remove(role_mgr.get(code=getattr(role, 'code', role)))
            
        else:
            if not (group or context):
                raise ValueError(u'You must provide a role or a group '\
                                 u'AND a context')
        
            group_name = getattr(group, 'name', group)
                
            ctype = ContentType.objects.get_for_model(context)
        
            group = Group.objects.get(name=group_name)
            role = role_mgr.get(group=group, context_type=ctype, 
                                             context_id=context.id)
            self.role_set.remove(role) 
       
            
    def is_registered(self):
        """
            Return wether a contact is registered or not.
        """
    
        return self.name and self.connection_set.count()
