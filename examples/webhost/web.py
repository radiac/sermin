"""
Common web definitions for all hosts
"""
from .nginx import Nginx, NginxSite


Nginx('/etc/nginx/nginx.conf')
NginxSite('default', '/var/www/default')
