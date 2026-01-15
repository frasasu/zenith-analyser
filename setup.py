#!/usr/bin/env python3
"""
Setup configuration for Zenith Analyser
"""

from setuptools import setup, find_packages

setup(
    name="zenith-analyser",
    version="1.0.0",
    author="Francois TUMUSAVYEYESU",
    author_email="frasasudev@gmail.com",
    description="A library for analyzing structured temporal laws",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
)
