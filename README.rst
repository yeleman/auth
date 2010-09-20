The auth app provides an interface for creating, updating,
and deleting RapidSMS contacts as rapidsms.contrib.registration does, but
allowing i18n for keywords and some special anwsers if the contact already
exists. It tries to provide some permissions management features as well,
following django.contrib.auth but adding the notion of 'role'.

The code is based on the one from rapidsms.contrib.registration and hence
share the same licence.

Features
=========

    - Ability to anwser in the same language than the keyword
    - Change name if the contact exists but the name is different
    - Tell the contact if he is already registered
    - The contact form includes an identity and a backend field
    - Set the contact language according to the keyword lang when registering
    - When you change the language, the answer is already in the new language

Depends on handlers_i18n, features and limitations apply.

Requirements
============

    - Django 1.2+
    - RapidSMS 1+ 
    - handlers_i18n (http://github.com/yeleman/handlers_i18n)
    - code_generator: http://github.com/yeleman/code_generator

Setup
=====

    - Install handlers_i18n (http://github.com/yeleman/handlers_i18n)
    - Put registration_ng dir somewhere in the Python PATH
    - Add 'registration_ng' to your INSTALLED_APPS
    - Removes 'rapidsms.contrib.registration' from INSTALLED_APPS and RAPIDSMS_TABS
    - Optionnally, add ("register_ng.views.registration", "Registration") to
      RAPIDSMS_TABS
    - Optionally, install 'django_simple_config' (http://github.com/yeleman/django-simple-config)
  
Usage
=====

In SMS::

    >> register Donald Duck 
    << Thank you for registering, Donald Duck!
    >> inscription Tintin
    << Merci de vous être enregistré, Tintin!
    >> lang english
    << I will speak to you in English
    >> register Milou
    << We changed your name from, 'Tintin' to 'Milou' 

/!\ By default, the keyword language always override the contact language
except when switching the language. To change this behavior, set in settings.py::

    RAPIDSMS_REGISTRATION_AUTO_SET_LANG = False
    RAPIDSMS_LANGUAGES_AUTO_SET_LANG = False

You can add your translations in the regular django translation dir.

If you want to add translationa or aliases for keywords, set in settings.py::

    RAPIDSMS_(REGISTRATION|LANGUAGES)_ALIASES = (
                                                    ('language_code1', (alias_1, alias_2)),
                                                    ('language_code2', (alias_1, alias_2)),
                                                 )

E.g::

    RAPIDSMS_LANGUAGES_ALIASES = (
                                    ('en-us', ('lang', 'dialect')),
                                    ('es', ('lingua',)),
                                  )

Closing registrations
=====================
                                  
If django_simple_config is installed, you will be able to set configuration
values in the Django admin. Set a value 'close_registrations' to the string
"1" (without quotes) to close the registration, and to "0" to reopen them.

Without django_simple_config, the registrations will simply stay always open.

TODO
=====

Roles contraints
-----------------

    - this role can be added only if you/somebody have this role
    - this role can be added only if you/somebody don't have this role
    - function to check if a role can be added or deleted

Password management
----------------------


    - some SMS like >> pwd blob
                    >> register  name username role rolecode pwd Blob
                    >> register  name username role group context
                    >> register  name username roles rolecode rolecode rolecode 
    
    - if password is sent, it is obfuscated in logger and later messages
    - reponds : "your new password is 'XXX' (obfuscate in logger),
                 remember to delete all sms containg your password in your 
                 inbox AND outbox check that this password is the right one"
    
    - change password
    





TODO
=====

Roles contraints
-----------------

    - this role can be added only if you/somebody have this role
    - this role can be added only if you/somebody don't have this role
    - function to check if a role can be added or deleted

Password management
----------------------


    - some SMS like >> pwd blob
                    >> register  name username role rolecode pwd Blob
                    >> register  name username role group context
                    >> register  name username roles rolecode rolecode rolecode 
    
    - if password is sent, it is obfuscated in logger and later messages
    - reponds : "your new password is 'XXX' (obfuscate in logger),
                 remember to delete all sms containg your password in your 
                 inbox AND outbox check that this password is the right one"
    
    - change password
    
