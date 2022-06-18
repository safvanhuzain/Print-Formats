from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in solo_learn/__init__.py
from solo_learn import __version__ as version

setup(
	name="solo_learn",
	version=version,
	description="self taught",
	author="safvanhuzain",
	author_email="safvanph41@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
