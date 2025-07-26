#!/usr/bin/env python3
"""
Setup script for Memory Bank MCP v2
"""

from setuptools import setup, find_packages

setup(
    name="memory-bank-mcp",
    version="2.0.0",
    description="Enhanced AI collaboration memory system with persistent database storage",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "aiosqlite>=0.19.0",
        "python-dateutil>=2.8.0"
    ],
    entry_points={
        "console_scripts": [
            "memory-bank-mcp=memory_bank_mcp.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
