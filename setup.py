"""Setup configuration for Brazilian CDS Data Feeder."""
from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README file
project_root = Path(__file__).parent
long_description = (project_root / "README.md").read_text() if (project_root / "README.md").exists() else ""

setup(
    name="brazilian-cds-feeder",
    version="1.0.0",
    description="Brazilian CDS (Credit Default Swap) data scraper and API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Flavio Lopes",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "pandas>=2.0.0",
        "requests>=2.28.0",
        "lxml>=4.9.0",
        "loguru>=0.7.0",
        "logtail-python>=0.3.0",
        "python-dotenv>=1.0.0",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "update-cds=scripts.update_cds:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
