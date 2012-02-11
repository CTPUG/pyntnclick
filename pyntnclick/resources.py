# -*- test-case-name: pyntnclick.tests.test_resources -*-

import os
from pkg_resources import resource_filename

import pygame


class ResourceNotFound(Exception):
    pass


class Resources(object):
    """Resource loader and manager.

    The `CONVERT_ALPHA` flag allows alpha conversions to be disabled so that
    images may be loaded without having a display initialised. This is useful
    in unit tests, for example.
    """

    DEFAULT_RESOURCE_MODULE = "pyntnclick.data"
    CONVERT_ALPHA = True

    def __init__(self, resource_module, language=None):
        self.resource_module = resource_module
        self.language = language
        self._image_cache = {}
        self._transformed_image_cache = {}

    def get_resource_path(self, *resource_path_fragments):
        """Find the resource in one of a number of different places.

        The following directories are searched, in order:

         * <resource_module>/<lang>/
         * <resource_module>/
         * <default_resource_module>/<lang>/
         * <default_resource_module>/

        If the `language` attribute is `None`, the paths with <lang> in them
        are skipped.
        """
        resource_name = '/'.join(resource_path_fragments)
        resource_name = os.path.join(*resource_name.split('/'))
        for path in self.get_paths(resource_name):
            if os.path.isfile(path):
                return path
        raise ResourceNotFound(resource_name)

    def get_paths(self, resource_path):
        """Get list of resource paths to search.
        """
        paths = []
        for module in [self.resource_module, self.DEFAULT_RESOURCE_MODULE]:
            if self.language:
                fn = os.path.join(self.language, resource_path)
                paths.append(resource_filename(module, fn))
            paths.append(resource_filename(module, resource_path))
        return paths

    def get_image(self, image_name_fragments, transforms=(), basedir='images'):
        """Load an image and optionally apply mutators.

        The `image_name_fragments` parameter may be either a string or a list
        of strings. The latter is a convenience for things that compose an
        image name out of several fragments.

        The `transforms` param may contain transforms, which modify an image
        in-place to apply various effects.

        The `basedir` param defaults to 'images', but may be overriden to load
        images from other places. ('icons', for example.)
        """

        # Juggle our various params and find an appropriate image path.
        if isinstance(image_name_fragments, basestring):
            image_name_fragments = [image_name_fragments]
        image_path = self.get_resource_path(basedir, *image_name_fragments)

        key = (image_path, transforms)
        if key in self._transformed_image_cache:
            # We already have this cached, so shortcut the whole process.
            return self._transformed_image_cache[key]

        if image_path not in self._image_cache:
            image = pygame.image.load(image_path)
            if self.CONVERT_ALPHA:
                image = image.convert_alpha(pygame.display.get_surface())
            self._image_cache[image_path] = image
        image = self._image_cache[image_path]

        # Apply any transforms we're given.
        for transform in transforms:
            image = transform(image)
        self._transformed_image_cache[key] = image

        return image
