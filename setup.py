# -*- coding: utf-8 -*-

import setuptools

from inventree_niimbot.version import NIIMBOT_PLUGIN_VERSION

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-niimbot-plugin",

    version=NIIMBOT_PLUGIN_VERSION,

    author="piramja",

    author_email="info@piramja.de",

    description="Niimbot label printer (b1, b18, b21, d11, d110) plugin for InvenTree",

    long_description=long_description,

    long_description_content_type='text/markdown',

    keywords="inventree inventreeplugins label printer printing inventory",

    url="https://github.com/piramja/inventree-niimbot-plugin",

    license="MIT",

    packages=setuptools.find_packages(),

    install_requires=[
        'bleak==0.21.1',
        'devtools==0.12.2',
        'setuptools==69.5.1',
        'markdown-it-py==3.0.0',
        'loguru==0.7.2',
        'pillow==10.3.0',
    ],

    setup_requires=[
        "wheel",
        "twine",
    ],

    python_requires=">=3.10",

    entry_points={
        "inventree_plugins": [
            "NiimbotLabeLPlugin = inventree_niimbot.niimbot_plugin:NiimbotLabelPlugin"
        ]
    },
)
