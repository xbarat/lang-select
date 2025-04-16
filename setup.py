#!/usr/bin/env python3
"""
Setup script for lang-select package.
"""

import os
from setuptools import setup, find_packages

# Read the contents of the README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lang-select",
    version="0.5.0",  # Updated version
    description="Tool to extract and select items from language model responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="barath",
    author_email="trybarath@gmail.com",
    url="https://github.com/xbarat/lang-select",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    extras_require={
        "rich": ["rich>=12.0.0"],
        "textual": ["textual>=0.38.0"],
        "all": ["rich>=12.0.0", "textual>=0.38.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "lang-select=lang_select.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 