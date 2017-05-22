"""
File management
"""
from builtins import str
import io
import os
from shutil import copyfile

import configparser
from future.utils import python_2_unicode_compatible
from jinja2 import Template
from six import string_types, StringIO

from ...constants import Undefined
from ..base import State


class FileParser(object):
    """
    Abstract base class for File parsers
    """
    class KeyError(Exception):
        """
        Raised when .get on a missing key without a default
        """
        pass

    def __init__(self, content):
        self.content = content

    def get(self, key, default=Undefined):
        if default != Undefined:
            return default
        raise KeyError('Key {} not found'.format(key))

    def is_set(self, key):
        try:
            self.get(key)
        except self.KeyError:
            return False
        else:
            return True

    def set(self, key, value):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def check(self, set, delete):
        """
        Check if there are any changes to make
        """
        if set:
            for key, new_value in set.items():
                try:
                    current_value = self.get(key)
                except self.KeyError:
                    return False
                if new_value != current_value:
                    return False

        if delete:
            for key in delete:
                if self.is_set(key):
                    return False

        return True

    def apply(self, set, delete):
        """
        Apply changes
        """
        if set:
            for key, value in set.items():
                self.set(key, value)

        if delete:
            for key in delete:
                self.delete(key)

    def render(self):
        raise NotImplementedError()


class AppendParser(FileParser):
    """
    Ensure that content exists, otherwise append it to the file

    The `set` argument should be a list of [line, line], although it can be a
    dict of {match: line} to conform with other parser syntax.

    Usage:

        File(
            path,
            parser=AppendParser,
            set=['Line 1', 'Line 2'],
            delete=['Line 3'],
        )
    """
    line_ending = str('\n')

    def __init__(self, *args, **kwargs):
        super(AppendParser, self).__init__(*args, **kwargs)
        if self.content:
            self.lines = self.content.split(self.line_ending)
        else:
            self.lines = []

    def get(self, key, default=Undefined):
        if key not in self.lines:
            return super(AppendParser, self).get(key, default)
        return key

    def set(self, key, value):
        if str(key) not in self.lines:
            self.lines.extend(str(value).split(self.line_ending))

    def delete(self, key):
        if str(key) in self.lines:
            self.lines.remove(str(key))

    def apply(self, set, delete):
        if set and not isinstance(set, dict):
            set = {line: line for line in set}
        super(AppendParser, self).apply(set, delete)

    def render(self):
        return self.line_ending.join(self.lines)


class IniParser(FileParser):
    """
    Wrapper for Python's standard ConfigParser for Windows-style INI files

    In Python 2 this uses the configparser backport, to support unicode

    Set and delete take tuples of (section, option). Delete can also take a
    string to refer to a section.

    Usage:

        File(
            path,
            parser=IniParser,
            set={
                ('Section', 'Option'): 'Value',
            }
            delete=[
                'Section',
                ('Section', 'Option'),
            ],
        )
    """
    def __init__(self, *args, **kwargs):
        super(IniParser, self).__init__(*args, **kwargs)
        self.config = configparser.RawConfigParser(
            allow_no_value=True,
        )
        self.config.read_string(self.content)

    def get(self, key, default=Undefined):
        section, option = key
        try:
            value = self.config.get(section, option)
        except configparser.NoOptionError:
            return super(IniParser, self).get(key, default)
        else:
            return value

    def set(self, key, value):
        section, option = key
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def delete(self, key):
        if isinstance(key, string_types):
            if self.config.has_section(key):
                self.config.remove_section(key)
                return True
            return False
        section, option = key
        return self.config.remove_option(section, option)

    def render(self):
        file = StringIO()
        self.config.write(file)
        return file.getvalue()


@python_2_unicode_compatible
class File(State):
    """
    Create or modify a file
    """
    # States
    EXISTS = 'exist'
    ABSENT = 'absent'

    def __init__(
        self, path, state=EXISTS, content=None, source=None,
        parser=None, set=None, delete=None, context=None,
        **kwargs
    ):
        """
        Define the file state

        Arguments:
            path        The path for this file
            state       The desired file state; one of:
                            File.EXISTS
                                The file will be created if it does not exist.
                            File.ABSENT
                                The file will be remove if it does exist.
                                No other arguments can be provided.
            content     A string to be used as content for this file. Cannot be
                        used with `source`.
            source      The source on disk. This can be absolute, or relative
                        to Sermin base dir. Cannot be used with `content`.
            parser      A FileParser subclass to manage the file
            set         Dict of key/value pairs to pass to the parser's `set()`
                        method. Requires `parser` - see parser class for more
                        details.
            delete      List of keys to pass to the parser's `delete()` method.
                        Requires `parser` - see parser class for more details.
            context     A dict of values to be passed into a Jinja template.
                        This is applied after `changes.
                        If `None`, the content is not treated as a template; to
                        process with an empty context set this to `{}`.
                        Can only be used with `source` or `content`.

        If content or source are missing, the file with be touched if it does
        not exist, and the replacements will be made on the file in place.
        """
        super(File, self).__init__(**kwargs)

        if state not in (self.EXISTS, self.ABSENT):
            raise ValueError('Invalid state')

        if (
            state == self.ABSENT and
            any((content, source, set, delete, context))
        ):
            raise ValueError(
                'A File defined in state ABSENT cannot take other arguments'
            )

        if parser is None and any((set, delete)):
            raise ValueError('A File needs a parser to set or delete')

        if content and source:
            raise ValueError(
                'A File can only be defined with a content or source, not both'
            )

        if context is not None and not (content or source):
            raise ValueError(
                'A File can only apply a context to a content or source'
            )

        self.path = path
        self.state = state
        self.content = content
        self.source = source
        self.parser = parser
        self.set = set
        self.delete = delete
        self.context = context

        # TODO: Accept relative source path
        # TODO: Ownership
        # TODO: Permissions

    def __str__(self):
        return self.path

    def read(self, path):
        with io.open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    def check(self):
        """
        Check fails if either the file doesn't exist, or it needs to be changed
        """
        self.state_exists = os.path.exists(self.path)

        # Trying to remove the file is simple - if it exists we need to change,
        # otherwise no change needed
        if self.state == self.ABSENT:
            if self.state_exists:
                self.report.debug('Exists but should not')
            else:
                self.report.debug('Does not exist')
            return not self.state_exists

        # We're always going to need to change it if the file doesn't exist
        if not self.state_exists:
            self.report.debug('Does not exist')
            return False

        # Find the current content of the file
        original = self.read(self.path)

        # Find the source content of the file
        content = ''
        if self.content is not None:
            content = self.content
        elif self.source:
            content = self.read(self.source)
        else:
            content = original

        # Check for changes
        if self.set or self.delete:
            parser = self.parser(content)
            if not parser.check(set=self.set, delete=self.delete):
                self.report.debug('Requires changes')
                return False

        # Check templates
        if self.context is not None:
            if original != self.render(content):
                self.report.debug('Requires rendering')
                return False

        return True

    def apply(self):
        # See if we need to remove the file
        if self.state == self.ABSENT:
            if self.state_exists:
                self.report.info('Removing file')
                os.remove(self.path)
            return

        # Copy the file, or ensure it exists
        if self.source:
            self.report.info('Copying from {}'.format(self.source))
            copyfile(self.source, self.path)
        elif not self.state_exists:
            self.report.info('Creating empty file')
            open(self.path, 'a').close()

        # Can finish now if there are no changes to make
        if (
            self.content is None and
            not self.set and
            not self.delete and
            self.context is None
        ):
            self.report.info('No content write required')
            return

        # Find the content
        if self.content is not None:
            content = self.content
        elif self.source:
            content = self.read(self.source)
        else:
            content = self.read(self.path)

        # Apply changes
        if self.set or self.delete:
            parser = self.parser(content)
            parser.apply(set=self.set, delete=self.delete)
            content = parser.render()

        if self.context:
            content = self.render(content)

        # Write content
        self.report.info('Writing content')
        with io.open(self.path, 'w') as file:
            file.write(str(content))

    def render(self, raw):
        template = Template(raw)
        return template.render(**self.context)
