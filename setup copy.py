from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cursor-agent',
    version='0.1.0',
    description='A Python-based AI agent that replicates Cursor\'s coding assistant capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nifemi Alpine',
    author_email='hello@civai.co',
    url='https://github.com/civai-technologies/cursor-agent',
    packages=find_packages(exclude=['tests*', 'examples*']),
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'black>=23.0.0',
            'isort>=5.0.0',
            'bump2version>=1.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
) 