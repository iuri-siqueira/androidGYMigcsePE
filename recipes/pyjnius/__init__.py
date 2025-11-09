"""
Custom pyjnius recipe with Python 3.11 compatibility
Uses pyjnius 1.7.0+ which has built-in Python 3.11 support
"""

from pythonforandroid.recipe import CythonRecipe


class PyjniusRecipe(CythonRecipe):
    """
    PyJNIus recipe with Python 3.11 compatibility
    Uses version 1.7.0+ which includes native Python 3.11 support
    """
    name = 'pyjnius'
    # Use 1.7.0 or later - these versions have Python 3.11 support built-in
    version = '1.7.0'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.tar.gz'
    site_packages_name = 'jnius'
    depends = ['setuptools', 'cython']
    call_hostpython_via_targetpython = False
    # No patches needed - 1.7.0+ has Python 3.11 compatibility built-in

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        return env


recipe = PyjniusRecipe()
