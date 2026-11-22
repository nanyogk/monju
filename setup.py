from setuptools import find_packages, setup

setup(
    name="monju",
    version="0.1.0",
    packages=find_packages(include=["monju*"]),
    package_data={"monju": ["generator/templates/*.html"]},
    entry_points={"console_scripts": ["monju=monju.cli:main"]},
)
