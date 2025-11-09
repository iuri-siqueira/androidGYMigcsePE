"""
Custom pyjnius recipe with Python 3.11 compatibility
Forces latest master branch with fixes for 'long' type issue
"""

from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.util import current_directory
from os.path import join, dirname
import sh


class PyjniusRecipe(CythonRecipe):
    """
    PyJNIus recipe with Python 3.11 compatibility fixes
    Applies patch to replace 'long' with 'int' for Python 3.11+
    """
    name = 'pyjnius'
    version = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    site_packages_name = 'jnius'
    depends = ['setuptools', 'cython']
    call_hostpython_via_targetpython = False
    patches = ['python311_compat.patch']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        # Ensure compatibility flags for Python 3.11
        return env


recipe = PyjniusRecipe()
