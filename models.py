"""
CS 562 - Query Processing Engine for EMF Queries
This module defines Phi class
based on the Phi operator specification.

Author: Rangasai Kumbhashi Raghavendra
CWID: 20028768
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PhiOperator:
    """
    Define Phi Data structure.

    """
    S: List[str] = field(default_factory=list)
    N: int = field(default_factory=int)
    V: List[str] = field(default_factory=list)
    F: List[str] = field(default_factory=list)
    P: List[str] = field(default_factory=list)
    H: Optional[str] = None


