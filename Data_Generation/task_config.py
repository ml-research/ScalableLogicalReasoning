from dataclasses import dataclass
from typing import Union, Dict, Tuple

@dataclass
class TaskConfig:
    """
    Task configuration Theta = <Rsample, Rlen, B_pi, kappa>
    - Rsample: 'random' or 'llm-guided'
    - Rlen: rule length (number of body literals)
    - B_pi: either 'uniform' or 'mirror' or a dict mapping ground atom -> probability
    - kappa: tuple (kappa_pos, kappa_neg) desired number of positive/negative examples
    """
    Rsample: str = 'random'
    Rlen: int = 1
    B_pi: Union[str, Dict[str, float]] = 'uniform'
    kappa: Tuple[int, int] = (1, 1)

    def validate(self):
        if self.Rsample not in ('random', 'llm-guided'):
            raise ValueError("Rsample must be 'random' or 'llm-guided-guided'")
        if not isinstance(self.Rlen, int) or self.Rlen < 1:
            raise ValueError("Rlen must be positive integer")
        if isinstance(self.B_pi, str) and self.B_pi not in ('uniform', 'mirror'):
            raise ValueError("B_pi string must be 'uniform' or 'mirror'")
        if not (isinstance(self.kappa, tuple) and len(self.kappa) == 2):
            raise ValueError("kappa must be a tuple (kappa_pos, kappa_neg)")

    def __repr__(self):
        return (f"TaskConfig(Rsample={self.Rsample}, Rlen={self.Rlen}, B_pi={self.B_pi}, "
                f"kappa={self.kappa})")
