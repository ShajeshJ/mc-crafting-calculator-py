from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Type
from .base_item import BaseItem
from math import ceil


class CraftableItem(BaseItem):
    TYPE = "craftable"

    def __init__(
        self,
        id: str,
        label: str,
        craft_amt: int,
        raw_craft_costs: Dict[str, int],
    ) -> None:
        super().__init__(id, label)
        self.craft_amt = craft_amt
        self._raw_craft_costs = raw_craft_costs
        self.craft_costs: Optional[Dict[BaseItem, int]] = None

    @classmethod
    def validate_definition(cls, d: Dict[str, Any]):
        super().validate_definition(d)

        missing_keys = set(["craft_amt", "raw_craft_costs"]) - d.keys()
        if missing_keys:
            raise Exception(f"Missing keys {missing_keys} from definition {d}")

        craft_amt = d["craft_amt"]
        raw_craft_costs = d["raw_craft_costs"]

        if craft_amt < 1:
            raise Exception(f"Invalid craft_amt: Cannot be < 1. Definition: {d}")

        if not raw_craft_costs and not isinstance(raw_craft_costs, dict):
            raise Exception(
                f"Invalid raw_craft_costs: Must be map of <item,amount>. Definition: {d}"
            )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        cls.validate_definition(d)
        return cls(
            id=d["id"],
            label=d["label"],
            craft_amt=d["craft_amt"],
            raw_craft_costs=d["raw_craft_costs"],
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "craft_amt": self.craft_amt,
            "raw_craft_costs": self._raw_craft_costs,
        }

    def build_craft_costs(self, all_items: Dict[str, BaseItem]):
        try:
            self.craft_costs = {
                all_items[item_str]: amt
                for item_str, amt in self._raw_craft_costs.items()
            }
        except KeyError as e:
            missing_items = self._raw_craft_costs.keys() - all_items.keys()
            raise RuntimeError(
                (
                    f"Missing definition for items {missing_items} "
                    f"required in crafting recipe for {str(self)}"
                )
            ) from e

    def get_craft_cost(self, amount: int) -> Tuple[Dict[BaseItem, int], int]:
        if self.craft_costs is None:
            raise RuntimeError(
                f"Craft costs missing for {str(self)}. Must call `item.build_craft_costs` first"
            )

        if amount < 0:
            raise RuntimeError(f"Must specify a craft amount >= 0")

        num_crafts = ceil(amount / self.craft_amt)
        excess = num_crafts * self.craft_amt - amount

        return {
            item: amt * num_crafts for item, amt in self.craft_costs.items()
        }, excess
