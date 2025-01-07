from enum import Enum


class ExecutionMode(Enum):
    LOCAL = "local"
    CLOUD = "cloud"


class Env(Enum):
    DEV = "dev"
    PRE = "pre"
    PROD = "prod"
