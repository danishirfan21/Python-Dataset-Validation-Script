from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-data-validator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for validating multi-turn assistant conversation datasets for LLM training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agent-data-validator",
    py_modules=["validator"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "agent-data-validator=validator:main",
        ],
    },
)