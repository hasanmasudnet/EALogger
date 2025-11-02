"""
Setup configuration for EALogger package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version
version_file = Path(__file__).parent / "src" / "EALogger" / "__init__.py"
version = "0.2.0"  # Default version

if version_file.exists():
    for line in version_file.read_text(encoding="utf-8").split("\n"):
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="EALogger",
    version=version,
    description="Enhanced Async Logging for FastAPI Projects with JSON formatting, performance tracking, and async support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hasan Masud",
    author_email="hasanmasudnet@example.com",
    url="https://github.com/hasanmasudnet/EALogger",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies - minimal for basic functionality
        # JSON library will be used if available, but not required
    ],
    extras_require={
        "fast": [
            "orjson>=3.11.0",  # For 3-5x faster JSON parsing
        ],
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
            "ruff>=0.4.0",
        ],
        "all": [
            "orjson>=3.11.0",
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
            "ruff>=0.4.0",
        ],
    },
    entry_points={
        # No CLI tools for now
    },
)

