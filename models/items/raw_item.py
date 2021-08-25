from typing import Dict, Tuple
from .base_item import BaseItem


class RawItem(BaseItem):
    TYPE = "raw"

    def __init__(self, id: str, label: str) -> None:
        super().__init__(id, label)

    def get_craft_cost(self, amount: int) -> Tuple[Dict[BaseItem, int], int]:
        return {self: amount}, -1
