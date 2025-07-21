"""To handle all the configuration related to the projects."""

import os
from enum import Enum
from dotenv import load_dotenv
from setuptools._distutils.util import strtobool


# load the environments variable from .env file located at root of the project.
dotenv_path = os.path.join(os.getcwd(), ".env")
env = load_dotenv(dotenv_path=dotenv_path, override=True)


class BaseConfiguration(Enum):
    """To manage all the base configuration of the project."""

    DEBUG = bool(strtobool(os.getenv("DEBUG", "False")))
    SECRET_KEY = os.getenv("SECRET_KEY")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
