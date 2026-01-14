"""
Setup script for BlackMamba Cognitive Core
"""
from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

with open('requirements-dev.txt') as f:
    dev_requirements = [
        line.strip() 
        for line in f 
        if line.strip() and not line.startswith('#') and not line.startswith('-r')
    ]

# Read README for long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='blackmamba-cognitive-core',
    version='0.1.0',
    author='BlackMamba',
    author_email='blackmvmba88@example.com',
    description='Motor cognitivo modular para construir aplicaciones interactivas basadas en IA',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Blackmvmba88/blackmamba-cognitive-core',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*', 'docs', 'scripts']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    entry_points={
        'console_scripts': [
            'blackmamba-serve=blackmamba.api.app:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
