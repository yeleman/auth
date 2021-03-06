#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as __
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import m2m_changed
from django.template.defaultfilters import slugify

from rapidsms.models import Contact

from code_generator.fields import CodeField


class RoleManager(models.Manager):

    def match(self, role=None, group=None, context=None):
        """
            Filter according to role/role code or group/group name or context.
        """
        
        roles = self.all()
        
        if role:
            roles = roles.filter(code=getattr(role, 'code', role))
        else:
            if not (group or context):
                raise ValueError(u'This method expects at least one argument')
            
            if group:
                roles = roles.filter(group__name=getattr(group, 'name', group))
            
            if context:
                ctype = ContentType.objects.get_for_model(context)
                roles = roles.filter(context_type=ctype, context_id=context.id)
            
        return roles
        
    # todo: test create
    def get_role(self, role=None, group=None, context=None, create=False):
        """
            Returns the role matching role/role code or group/group name AND
            context
        """
        
        if not role and not (group and context):
            raise ValueError(u'This method expects role or group AND context')
         
        if not create:   
            return self.match(role, group, context).get()
            
        if not (group or context):
            raise ValueError(u'You must provide a role or a group '\
                             u'AND a context') 

        gr_name = getattr(group, 'name', group)
        ctype = ContentType.objects.get_for_model(context)

        group, group_created = Group.objects.get_or_create(name=gr_name)
        
        role, role_created = Role.objects.get_or_create(group=group,
                                                        context_type=ctype, 
                                                        context_id=context.id)

        return role, role_created, group_created



class Role(models.Model):
    
    code = CodeField(verbose_name=__("Code"),  max_length=12, prefix='r')
    contacts = models.ManyToManyField(Contact, verbose_name=__(u'Contacts'))
    group = models.ForeignKey(Group, verbose_name=__(u'Group'), 
                              related_name='roles')
    context_type = models.ForeignKey(ContentType, related_name='roles')
    context_id = models.PositiveIntegerField()
    context = generic.GenericForeignKey('context_type', 'context_id')
    
    objects = RoleManager()
    
    class Meta:
        unique_together = (("context_type", "context_id", "group"),)

    
    def has_contact(self, contact=None):
        """
            Check if a this contact has this role. If no contact is given,
            check if any contact has this role.
        """
        contacts = self.contacts.all()
        if contact:
            contacts = contacts.filter(pk=contact.pk)
        return contacts.exists()
        
    
    def __unicode__(self):
        return _(u"%(group)s (%(context)s)") % {
                 'group': _(unicode(self.group)),
                 'context': _(unicode(self.context))}
      
      
    @classmethod
    def update_user_contact_groups(cls, *args, **kwargs):
        """
            Udate the user groups to match the contact roles group
            
            Please not that if the user has no more roles associated to
            a group, the user is removed fromt the group.
            
            Don't add a user to a group used in roles directly
        """
        
        action = kwargs['action']
        
        # map (post|pre)_* actions to (post|pre)_*_m2m classmethods
        
        if action in ('post_add', 'post_remove', 'pre_clear'):
            getattr(cls, action + '_m2m')(instance=kwargs['instance'],
                                         pk_set=kwargs['pk_set'],
                                         reverse=kwargs['reverse'])
        

    @classmethod
    def post_add_m2m(cls, instance, pk_set, reverse):   
        """
            Add the contact user into the role group
        """
        if reverse: # we are calling contact.role_set.add(role, role, ...)
            
            # instance is the contact
            user = instance.user
            
            # pk_set contains ids for all the roles been passed
            for role_id in pk_set:
                role = Role.objects.get(pk=role_id)
                user.groups.add(role.group)
            
        else: # we are calling role.contacts.add(contact, contact, ...)
           
            # instance is the role
            group = instance.group
            
             # pk_set contains ids for all the contacts been passed
            for contact_id in pk_set:
                user = Contact.objects.get(pk=contact_id).user
                user.groups.add(group)
                    
    
    @classmethod
    def post_remove_m2m(cls, instance, pk_set, reverse):   
        """
            Remove the contact user from the role group if he is not
            having any role with such a group
        """
        
        if reverse: # we are calling contact.role_set.remove(role, role, ...)
            
            # instance is the contact
            user = instance.user
            
            # pk_set contains ids for all the roles been passed
            for role_id in pk_set:
                role = Role.objects.get(pk=role_id)
                group = role.group
                if not instance.role_set.filter(group=group).exists():
                    user.groups.remove(group)
            
        else: # we are calling role.contacts.remove(contact, contact, ...)
           
            # instance is the role
            group = instance.group
            
             # pk_set contains ids for all the contacts been passed
            for contact_id in pk_set:
                contact = Contact.objects.get(pk=contact_id)
                if not contact.role_set.filter(group=group).exists():
                    contact.user.groups.remove(group)


    @classmethod
    def pre_clear_m2m(cls, instance, pk_set, reverse):   
        """
            Remove the contact user from all its roles groups
            of remove the role group from all its contacts
        """
        
        if reverse: # we are calling contact.role_set.remove(role, role, ...)
            for role in instance.role_set.all(): # instance is the contact
                instance.user.groups.remove(role.group)
            
        else: # we are calling role.contacts.remove(contact, contact, ...)
            for contact in instance.contacts.all(): # instance is the role
                group = instance.group
                if not contact.role_set.exclude(pk=instance.pk)\
                                    .filter(group=group).exists():
            
                    contact.user.groups.remove(group)
                

m2m_changed.connect(Role.update_user_contact_groups, sender=Role.contacts.through)
