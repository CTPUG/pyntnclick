import os.path
from unittest import TestCase

from pyntnclick.resources import Resources


TEST_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(os.path.dirname(TEST_PATH), 'data')

test_path = lambda p: os.path.join(TEST_PATH, p)
data_path = lambda p: os.path.join(DATA_PATH, p)


class ResourcesTestCase(TestCase):
    def test_get_paths_no_lang(self):
        res = Resources('pyntnclick.tests')
        self.assertEqual([test_path('thing'), data_path('thing')],
                         res.get_paths('thing'))

    def test_get_paths_lang(self):
        res = Resources('pyntnclick.tests', 'en')
        self.assertEqual([test_path('en/thing'), test_path('thing'),
                          data_path('en/thing'), data_path('thing')],
                         res.get_paths('thing'))
