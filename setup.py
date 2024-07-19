from setuptools import setup, find_packages

setup(
    name='maryland_crime_analysis',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pandas',
        'seaborn',
        'matplotlib',
        'altair',
        'plotly',
        'unittest'
    ],
    entry_points={
        'console_scripts': [
            'maryland-crime-analysis=app.main:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A Streamlit app for analyzing Maryland crime data.',
    url='https://github.com/yourusername/maryland-crime-analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
