#!/usr/bin/env python3
"""
Setup script for Air Overhead - Local Flight Tracker
A real-time flight tracking application with Vestaboard integration
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="air-overhead",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A real-time flight tracking application with Vestaboard integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/air-overhead",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "air-overhead=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.json", "*.md"],
    },
    keywords="flight tracking, aviation, opensky, vestaboard, real-time",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/air-overhead/issues",
        "Source": "https://github.com/yourusername/air-overhead",
        "Documentation": "https://github.com/yourusername/air-overhead#readme",
    },
)