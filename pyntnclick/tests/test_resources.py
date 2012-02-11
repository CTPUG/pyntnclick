import os.path
from unittest import TestCase

from pygame.surface import Surface

from pyntnclick.resources import Resources, ResourceNotFound


TEST_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(os.path.dirname(TEST_PATH), 'data')

test_path = lambda p: os.path.join(TEST_PATH, p)
data_path = lambda p: os.path.join(DATA_PATH, p)


class ResourcesTestCase(TestCase):
    def setUp(self):
        self.res = self.get_resource_loader()

    def get_resource_loader(self, *args, **kw):
        res = Resources('pyntnclick.tests', *args, **kw)
        res.CONVERT_ALPHA = False  # Because we have no display.
        return res

    def test_get_paths_no_lang(self):
        self.assertEqual([test_path('thing'), data_path('thing')],
                         self.res.get_paths('thing'))

    def test_get_paths_lang(self):
        res = self.get_resource_loader('en')
        self.assertEqual([test_path('en/thing'), test_path('thing'),
                          data_path('en/thing'), data_path('thing')],
                         res.get_paths('thing'))

    def test_get_resource_path_missing(self):
        try:
            self.res.get_resource_path('should_not_exist')
            self.fail('Expected ResourceNotFound error.')
        except ResourceNotFound, e:
            self.assertEqual('should_not_exist', e.args[0])

    def test_get_resource_path_in_test(self):
        self.assertEqual(test_path('test_resources.py'),
                         self.res.get_resource_path('test_resources.py'))

    def test_get_resource_path_in_data(self):
        self.assertEqual(
            data_path('images/pyntnclick/hand.png'),
            self.res.get_resource_path('images/pyntnclick/hand.png'))

    def test_load_image(self):
        image = self.res.load_image('pyntnclick/hand.png')
        self.assertTrue(isinstance(image, Surface))

    def test_load_image_fragments(self):
        image = self.res.load_image(['pyntnclick', 'hand.png'])
        self.assertTrue(isinstance(image, Surface))

    def test_load_image_different_basedir(self):
        image = self.res.load_image('hand.png', basedir='images/pyntnclick')
        self.assertTrue(isinstance(image, Surface))

    def test_load_missing(self):
        try:
            self.res.load_image('should_not_exist')
            self.fail('Expected ResourceNotFound error.')
        except ResourceNotFound, e:
            self.assertEqual('images/should_not_exist', e.args[0])
