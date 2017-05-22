"""
Test the Command state
"""
import os

from sermin import File, AppendParser, IniParser
from sermin.utils import shell

from .utils import FullTestCase


class FileMixin(object):
    # Path to use for file test
    path = '/tmp/sermin_test'
    path_src = '/tmp/sermin_test_src'

    def clean(self):
        """
        Ensure file is not on the system
        """
        shell('rm -rf {}'.format(self.path))
        shell('rm -rf {}'.format(self.path_src))

    def read(self):
        with open(self.path) as file:
            content = file.readlines()
        return content


class FileTest(FileMixin, FullTestCase):
    def test_content_creates(self):
        File(self.path, content='Test content')
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test content')

    def test_content_copies(self):
        File(self.path_src, content='Test content')
        File(self.path, source=self.path_src)
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test content')

    def test_absent_deletes(self):
        shell('touch {}'.format(self.path))
        self.assertTrue(os.path.exists(self.path))
        File(self.path, state=File.ABSENT)
        self.registry_run()
        self.assertFalse(os.path.exists(self.path))

    def test_content_context(self):
        File(self.path, content='Test {{ arg }} complete', context={
            'arg': 'text_content_context',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test text_content_context complete')

    def test_source_context(self):
        File(self.path_src, content='Test {{ arg }} complete')
        File(self.path, source=self.path_src, context={
            'arg': 'test_source_context',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test test_source_context complete')

    def test_invalid_state_raises(self):
        with self.assertRaisesRegexp(ValueError, r'^Invalid state$'):
            File(self.path, state='invalid')

    def test_absent_with_values_raises(self):
        for arg in ['content', 'source', 'set', 'delete', 'context']:
            with self.assertRaisesRegexp(
                ValueError,
                r'^A File defined in state ABSENT cannot take other arguments$'
            ):
                File(self.path, state=File.ABSENT, **{arg: True})

    def test_set_delete_missing_parser_raises(self):
        for arg in ['set', 'delete']:
            with self.assertRaisesRegexp(
                ValueError,
                r'^A File needs a parser to set or delete$'
            ):
                File(self.path, **{arg: True})

    def test_content_and_source_raises(self):
        with self.assertRaisesRegexp(
            ValueError,
            r'^A File can only be defined with a content or source, not both$'
        ):
            File(self.path, content='fail', source='fail')

    def test_context_missing_content_or_source_raises(self):
        with self.assertRaisesRegexp(
            ValueError,
            r'^A File can only apply a context to a content or source$'
        ):
            File(self.path, context={})


class FileAppendTest(FileMixin, FullTestCase):
    def test_set__new_line__new_file(self):
        File(self.path, parser=AppendParser, set=['Test content'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test content')

    def test_set__new_line__existing_file(self):
        File(self.path, content='Test content 1')
        File(self.path, parser=AppendParser, set=['Test content 2'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], 'Test content 1\n')
        self.assertEqual(content[1], 'Test content 2')

    def test_set__existing_line(self):
        File(self.path, content='Test content 1\nTest content 2')
        File(self.path, parser=AppendParser, set=['Test content 2'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], 'Test content 1\n')
        self.assertEqual(content[1], 'Test content 2')

    def test_delete__existing_line(self):
        File(self.path, content='Test content 1\nTest content 2')
        File(self.path, parser=AppendParser, delete=['Test content 2'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test content 1')

    def test_delete__missing_line__existing_file(self):
        File(self.path, content='Test content 1')
        File(self.path, parser=AppendParser, delete=['Test content 2'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0], 'Test content 1')


class FileIniTest(FileMixin, FullTestCase):
    def test_set__new_section__new_option__new_file(self):
        File(self.path, parser=IniParser, set={
            ('Test section', 'Test option'): 'Test value',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 3)
        self.assertEqual(content[0], '[Test section]\n')
        self.assertEqual(content[1], 'test option = Test value\n')
        self.assertEqual(content[2], '\n')

    def test_set__new_section__new_option__existing_file(self):
        File(self.path, content='[Section 1]\noption 1 = Value 1\n')
        File(self.path, parser=IniParser, set={
            ('Section 2', 'Option 2'): 'Value 2',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 6)
        self.assertEqual(content[0], '[Section 1]\n')
        self.assertEqual(content[1], 'option 1 = Value 1\n')
        self.assertEqual(content[2], '\n')
        self.assertEqual(content[3], '[Section 2]\n')
        self.assertEqual(content[4], 'option 2 = Value 2\n')
        self.assertEqual(content[5], '\n')

    def test_set__existing_section__new_option(self):
        File(self.path, content='[Section 1]\noption 1 = Value 1\n')
        File(self.path, parser=IniParser, set={
            ('Section 1', 'Option 2'): 'Value 2',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 4)
        self.assertEqual(content[0], '[Section 1]\n')
        self.assertEqual(content[1], 'option 1 = Value 1\n')
        self.assertEqual(content[2], 'option 2 = Value 2\n')
        self.assertEqual(content[3], '\n')

    def test_set__existing_option(self):
        File(self.path, content='[Section 1]\noption 1 = Value 1\n')
        File(self.path, parser=IniParser, set={
            ('Section 1', 'Option 1'): 'Value 2',
        })
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 3)
        self.assertEqual(content[0], '[Section 1]\n')
        self.assertEqual(content[1], 'option 1 = Value 2\n')
        self.assertEqual(content[2], '\n')

    def test_delete__existing_option__other_options(self):
        File(self.path, content=(
            '[Section 1]\n'
            'option 1 = Value 1\n'
            'option 2 = Value 2\n'
        ))
        File(self.path, parser=IniParser, delete=[('Section 1', 'option 1')])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 3)
        self.assertEqual(content[0], '[Section 1]\n')
        self.assertEqual(content[1], 'option 2 = Value 2\n')
        self.assertEqual(content[2], '\n')

    def test_delete__existing_option__only_option(self):
        File(self.path, content='[Section 1]\noption 1 = Value 1\n')
        File(self.path, parser=IniParser, delete=[('Section 1', 'option 1')])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], '[Section 1]\n')
        self.assertEqual(content[1], '\n')

    def test_delete__existing_section_with_options(self):
        File(self.path, content='[Section 1]\noption 1 = Value 1\n')
        File(self.path, parser=IniParser, delete=['Section 1'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 0)

    def test_delete__existing_section_empty(self):
        File(self.path, content='[Section 1]\n')
        File(self.path, parser=IniParser, delete=['Section 1'])
        self.registry_run()
        self.assertTrue(os.path.exists(self.path))
        content = self.read()
        self.assertEqual(len(content), 0)
