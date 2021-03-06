from setuptools import find_packages
from setuptools import setup

VERSION = "0.0.1"

with open("./README.md") as f:
    long_description = f.read()

setup_info = dict(
    name="flatland",
    version=VERSION,
    author="Maya Developer Team",
    author_email="humans@mayahq.com",
    url="https://github.com/mayahq/flatland",
    description="Turtle Program Synthesis Toy Problem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "jinja2==2.11.3",
        "numpy>=1.19.2",
        "pandas>=1.2.3",
        "networkx>=2.5.1",
        "Pillow>=8.3.1",
        "joblib>=1.0.1",
        "cliquematch>=3.0.0",
    ],
    extras_require={"full": ["graphviz"]},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "flatland-draw=flatland.cli.draw:main",
            "flatland-scoring=flatland.cli.scoring:main",
            "flatland-ddist=flatland.cli.domain_distance:main",
            "flatland-augment=flatland.cli.augment:main",
            "flatland-library=flatland.cli.show_library:main",
        ]
    },
)

setup(**setup_info)
