from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "CommitBot",
    version = "0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'commitbot = commitbot.app:main',
        ]
    },
    install_requires = ['wokkel', 'twisted', 'twisted-words', 'twisted-names']
)
