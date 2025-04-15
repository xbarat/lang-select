from setuptools import setup, find_packages

# Read the content of README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Extract and select items from language model responses"

setup(
    name="lang-select",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Tool to extract and select items from language model responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lang-select",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "rich": ["rich>=12.0.0"],
    },
    entry_points={
        "console_scripts": [
            "lang-select=lang_select.cli:main",
        ],
    },
) 