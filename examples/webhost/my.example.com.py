"""
Host definition for my.example.com
"""
from .nginx import NginxSite
from .web import *  # NOQA


NginxSite('my.example.com', '/var/www/my.example.com')
