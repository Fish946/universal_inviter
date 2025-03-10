from setuptools import setup, find_packages

setup(
    name="universal_inviter",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "telethon",
        "qasync"
    ]
) 