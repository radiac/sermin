import sermin
from sermin import File


#
# Simple definitions
#

foo = File('/tmp/foo')
bar = File('/tmp/bar')


@sermin.check
def custom_check():
    pass


@sermin.apply(listen=custom_check)
def custom_apply():
    pass
