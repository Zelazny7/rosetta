import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Zelazny7",  # Replace with your own username
    version="0.0.1",
    author="Eric E. Graves",
    author_email="gravcon5@gmail.com",
    description="Convert code specs into the language of your dreams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ins.risk.regn.net/minneapolis-python-users/rosetta",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
