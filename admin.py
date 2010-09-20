#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
# maintainer: dgelvin

'''
django.contrib.admin integration
'''

from django.contrib import admin
from .models import Role


class RoleAdmin(admin.ModelAdmin):
    '''
    Custom ModelAdmin to be used for the LoggedMessage field. Enables
    filtering, searching (name and text fields), and the slick built-in
    django date-higherarchy widget.
    '''
    
    search_fields = ['contact__name', 
                     'contact__user__first_name', 
                     'contact__user__last_name',
                     'contact__user__username',]
    
admin.site.register(Role, RoleAdmin)
