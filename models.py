from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PhiOperator:
    S: List[str] = field(default_factory=list)
    N: int = field(default_factory=int)
    V: List[str] = field(default_factory=list)
    F: List[str] = field(default_factory=list)
    P: List[str] = field(default_factory=list)
    H: Optional[str] = None


