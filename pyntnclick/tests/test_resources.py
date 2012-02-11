import os.path
from unittest import TestCase

from pygame.surface import Surface

from pyntnclick.resources import Resources, ResourceNotFound


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

    def test_get_resource_path_missing(self):
        res = Resources('pyntnclick.tests')
        try:
            res.get_resource_path('should_not_exist')
            self.fail('Expected ResourceNotFound error.')
        except ResourceNotFound, e:
            self.assertEqual('should_not_exist', e.args[0])

    def test_get_resource_path_in_test(self):
        res = Resources('pyntnclick.tests')
        self.assertEqual(test_path('test_resources.py'),
                         res.get_resource_path('test_resources.py'))

    def test_get_resource_path_in_data(self):
        res = Resources('pyntnclick.tests')
        self.assertEqual(data_path('images/pyntnclick/hand.png'),
                         res.get_resource_path('images/pyntnclick/hand.png'))

    def test_load_image(self):
        res = Resources('pyntnclick.tests')
        res.CONVERT_ALPHA = False
        image = res.load_image('pyntnclick/hand.png')
        self.assertTrue(isinstance(image, Surface))
