#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

try:
    from django_simple_config.models import Configuration
except ImportError:
    # it's not install, then you can't close registration
    def are_registrations_closed():
        return 0
else:
    
    def are_registrations_closed():
        return int(Configuration.get('close_registrations', "0"))
