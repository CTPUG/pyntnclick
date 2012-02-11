# -*- test-case-name: pyntnclick.tests.test_resources -*-

import os
from pkg_resources import resource_filename

import pygame


class ResourceNotFound(Exception):
    pass


class Resources(object):
    DEFAULT_RESOURCE_MODULE = "pyntnclick.data"
    CONVERT_ALPHA = True

    def __init__(self, resource_module, language=None):
        self.resource_module = resource_module
        self.language = language
        self._image_cache = {}

    def get_resource_path(self, *resource_path_fragments):
        resource_name = os.path.join(*resource_path_fragments)
        for path in self.get_paths(resource_name):
            if os.path.exists(path):
                return path
        raise ResourceNotFound(resource_name)

    def get_paths(self, resource_path):
        paths = []
        for module in [self.resource_module, self.DEFAULT_RESOURCE_MODULE]:
            if self.language:
                fn = os.path.join(self.language, resource_path)
                paths.append(resource_filename(module, fn))
            paths.append(resource_filename(module, resource_path))
        return paths

    def load_image(self, image_name):
        image_path = self.get_resource_path('images', image_name)
        if image_path not in self._image_cache:
            image = pygame.image.load(image_path)
            if self.CONVERT_ALPHA:
                image = image.convert_alpha(pygame.display.get_surface())
            self._image_cache[image_path] = image
        return self._image_cache[image_path]
