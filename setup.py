"""
Setup script for debug_utils package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="debug-utils",
    version="0.1.0",
    author="AI Debug Utils",
    author_email="your.email@example.com",
    description="Modular debugging utilities for AI training and inference workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/debug-utils",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "torch": ["torch>=1.9.0"],
        "pandas": ["pandas>=1.3.0"],
        "full": ["torch>=1.9.0", "pandas>=1.3.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "debug-utils-setup=debug_utils.utils:setup_debug_environment",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="debugging, ai, ml, pytorch, testing, development",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/debug-utils/issues",
        "Source": "https://github.com/yourusername/debug-utils",
        "Documentation": "https://github.com/yourusername/debug-utils/wiki",
    },
)
