"""Stair point-cloud generation and steppable-surface segmentation.

Mini Project - Sensor dan Sistem Pengolahan Sinyal.
"""

from .generate import StairParams, generate_stair_cloud, LABEL_TREAD, LABEL_RISER, LABEL_OTHER
from . import segment
from . import evaluate

__all__ = [
    "StairParams",
    "generate_stair_cloud",
    "LABEL_TREAD",
    "LABEL_RISER",
    "LABEL_OTHER",
    "segment",
    "evaluate",
]
