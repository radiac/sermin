"""
Load and run Sermin scripts
"""
from importlib import import_module
import os
import sys

from .state.base.registry import registry
from .config import settings


class Sermin(object):
    def __init__(self, blueprint, **settings_namespaces):
        """
        Initialise Sermin with the blueprint and any settings

        Settings must be provided in the format

            Sermin(blueprint, namespace={key: value, ...}, ...)
        """
        # Store the blueprint
        self.blueprint = blueprint

        # Load settings
        self.load_settings(settings_namespaces)

        # If the --host argument is set, we're not loading it here
        if settings.sermin.host:
            self.remote()
        else:
            # Load and initialise the blueprint
            self.load_blueprint()

    def load_settings(self, settings_namespaces):
        # Set global settings from self.settings
        for namespace_name, settings_dict in settings_namespaces.items():
            namespace = getattr(settings, namespace_name)
            for key, value in settings_dict.items():
                setattr(namespace, key, value)

    def load_blueprint(self):
        """
        Reset the registry and load a blueprint
        """
        registry.clear()

        # Prepare source
        source = settings.sermin.source
        if source:
            if (
                source.startswith('http://') or
                source.startswith('https://')
            ):
                self.source_http(source)

            elif source.startswith('git+ssh://'):
                self.source_git(source)

            elif os.path.isdir(source):
                self.source_dir(source)

        if self.blueprint.endswith('.py'):
            # ++ TODO
            # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
            raise NotImplementedError('No script support yet')
        else:
            import_module(self.blueprint)

    def source_http(self, source):
        raise NotImplementedError('No http support yet')
        # Download source to local_source, at ~/.sermin/source/
        # TODO
        self.source_dir(source)

    def source_git(self, source):
        raise NotImplementedError('No git support yet')
        # Download source to local_source, at ~/.sermin/source/
        # TODO
        self.source_dir(source)

    def source_dir(self, source):
        sys.path.append(source)
        # ++ change working directory

    def remote(self):
        raise NotImplementedError('No host support yet')
        # Use fabric to install sermin, push file (if necessary) and run

    def run(self):
        registry.run()
