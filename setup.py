import setuptools
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
        name="Luminos",
        version="0.0.1",
        author="Ascor",
        description="???",
        long_description=long_description,
        long_description_content_type="text/markdown",
        license='LICENSE.txt',
        url="",
        classifiers=[
                "Programming Language :: Python :: 3",
                "Operating System :: OS Independent",
                ],
        packages=find_packages(),
        python_requires=">=3.9",
        install_requires=[
                "pyqt5",
                "qt-material",
                ],
        )
