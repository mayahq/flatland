from setuptools import setup, find_packages

VERSION = "0.0.1"

with open("./README.md") as f:
    long_description = f.read()

setup_info = dict(
    name="flatland",
    version=VERSION,
    author="Maya Developer Team",
    author_email="humans@mayahq.com",
    url="https://github.com/mayahq/flatland",
    description="Data Generation for Turtle Program Synthesis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "jinja2==2.11.3",
        "numpy==1.19.2",
        "networkx==2.5.1",
        "Pillow==8.3.1",
    ],
    extras_require={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": []},
)

setup(**setup_info)
