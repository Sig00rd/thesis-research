from typing import Optional

class ReadabilityFactor:
    def __init__(self, name: str, weight: float, value: Optional[float]):
        self.name = name
        self.value = value
        self.weight = weight
