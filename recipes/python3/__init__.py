"""
Custom Python3 recipe that excludes Android-incompatible modules
Fixes compilation errors for grp, _lzma, pwd, and other non-Android modules
"""

from pythonforandroid.recipes.python3 import Python3Recipe as OriginalPython3Recipe


class Python3Recipe(OriginalPython3Recipe):
    """
    Extended Python3 recipe with Android-specific module exclusions
    """

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # Disable problematic modules that don't compile on Android
        env['PYTHON_DISABLE_MODULES'] = 'grp,_lzma,pwd,ossaudiodev,spwd,nis,_crypt,_uuid'

        return env


recipe = Python3Recipe()
