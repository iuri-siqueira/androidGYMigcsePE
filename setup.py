"""
Setup file for IGCSE GYM Android build
Ensures proper dependency configuration
"""
from setuptools import setup

setup(
    name='igcsegym',
    version='1.0',
    description='IGCSE GYM - Fitness Tracking App',
    author='IGCSE Team',
    py_modules=['main_android'],
    install_requires=[
        'kivy==2.2.1',
        'xlsxwriter',
    ],
    python_requires='>=3.11',
)
