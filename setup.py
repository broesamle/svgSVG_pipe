import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="svgpipe-BROESAMLE",
    version="0.0.1",
    author="Martin Brösamle",
    author_email="m@martinbroesamle.de",
    description="Modify existing SVG documents: inject/extract/map content.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/broesamle/svgpipe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    python_requires='>=3.7')