from setuptools import setup, find_packages

setup(
    name="sdm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "PyJWT>=2.8.0",
    ],
    entry_points={
        'console_scripts': [
            'sdm=signoz_cli.__main__:main',
        ],
    },
    author="Creator54",
    author_email="creator54@github.com",
    description="A minimal CLI tool for managing SigNoz dashboards",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/creator54/sdm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 