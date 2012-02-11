# -*- test-case-name: pyntnclick.tests.test_resources -*-

import os
from pkg_resources import resource_filename


class ResourceNotFound(Exception):
    pass


class Resources(object):
    DEFAULT_RESOURCE_MODULE = "pyntnclick.data"

    def __init__(self, resource_module, language=None):
        self.resource_module = resource_module
        self.language = language

    def get_resource_path(self, resource_name):
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
