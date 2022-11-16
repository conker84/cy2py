from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "ipython>=1.0",
    "neo4j>=4.4.5",
    "ipython-genutils>=0.1.0",
    "ipycytoscape>=1.3.3",
    "networkx"
]

setup(
    name="cy2py",
    version="1.1.2",
    author="Andrea Santurbano",
    author_email="santand@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conker84/cy2py",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=install_requires
)
