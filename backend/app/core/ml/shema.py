from enum import Enum


class ModelStatusEnum(str, Enum):
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVEd = "archived"


class ModelTypeEnum(str, Enum):
    GRADIENT_BOOSTING = "gradient_boosting"
