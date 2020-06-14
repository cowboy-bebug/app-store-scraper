import setuptools

about = dict()

with open("app_store_scraper/__version__.py", "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    install_requires = f.readlines()

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    url=about["__url__"],
    license=about["__license__"],
    keywords=about["__keywords__"],
    packages=setuptools.find_packages(".", exclude=["*.tests"]),
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.6",
    project_urls={"Source": about["__url__"]},
)
