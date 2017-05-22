"""
Nginx
"""
from sermin import State, Package, File


class Nginx(State):
    # Nested resources
    package = Package('nginx')

    def __init__(self, conf_path):
        # Resource based on settings
        self.conf = File(conf_path)
