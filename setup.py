"""Setup configuration for DXF Geo-processing Bot."""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='dxf-geoprocessing-bot',
    version='1.0.0',
    description='DXF geo-processing with relief densification',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DXF Geo Team',
    author_email='support@example.com',
    url='https://github.com/yourusername/dxf-geoprocessing-bot',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.24.0',
        'scipy>=1.10.0',
        'shapely>=2.0.0',
        'ezdxf>=1.1.0',
        'Pillow>=10.0.0',
        'requests>=2.31.0',
        'python-telegram-bot>=20.0',
        'pandas>=2.0.0',
        'chardet>=5.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'dxf-geo=cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='dxf gis surveying densification tin triangulation',
)
