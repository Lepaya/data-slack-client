import codecs
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "4.0"
DESCRIPTION = "Python slack client for Lepaya"
LONG_DESCRIPTION = "A package that allows to interact with the slack sdk and dynamically send messages to slack"

# Setting up
setup(
    name="data_slack_client",
    version=VERSION,
    author="Humaid Mollah",
    author_email="humaid.mollah@lepaya.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["slack-sdk~=3.19", "structlog~=22.3", "pydantic~=1.9", "pytz~=2024.1", "bumpversion"],
    keywords=["python", "slack", "message", "blocks", "dynamic"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Lepaya Python Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
