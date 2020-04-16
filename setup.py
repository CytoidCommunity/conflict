import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tairitsuru",
    version="0.1.0",
    description="The automatic Bilibili livestream capturing tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="live bilibili",
    url="https://github.com/CytoidCommunity/tairitsuru",
    entry_points={
        "console_scripts": [
            "tairitsuru=tairitsuru.cli:cli",
        ],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet"
    ],
    install_requires=[
        "click",
        "aioboto3"
    ],
    python_requires=">=3.7",
)