from setuptools import setup, find_packages

# Read the requirements.txt file for dependencies
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="Google Calendar Birthday Sync",
    version="0.1.0",
    description="Synchronize the birthdays of your Google Contacts with your Google Calendar",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Maik Basel",
    packages=find_packages(),
    include_package_data=True,  # Include data files specified in MANIFEST.in
    install_requires=requirements,  # Read dependencies from requirements.txt
    entry_points = {
        "console_scripts": [
            "bdays=gcal_bday_sync.cli:bdays",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
