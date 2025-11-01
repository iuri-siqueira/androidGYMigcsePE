from pythonforandroid.recipe import PythonRecipe


class XlsxwriterRecipe(PythonRecipe):
    """Recipe for xlsxwriter - pure Python Excel writer"""

    name = 'xlsxwriter'
    version = '3.1.9'
    url = 'https://pypi.python.org/packages/source/X/XlsxWriter/XlsxWriter-{version}.tar.gz'

    # Pure Python - no compilation needed
    call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = XlsxwriterRecipe()
