from __future__ import annotations
from typing import Any, Dict, Tuple, Type


class BaseItem:
    """Base class for all items. Should not be instantiated on its own.
    Instead new classes should inherit from this base class, in some module
    file within `models.items` and only instances of the subclasses should be instantiated
    """

    TYPE: str

    def __init__(self, id: str, label: str) -> None:
        self.__id = id
        self.label = label

    @property
    def id(self):
        return self.__id

    @classmethod
    def validate_definition(cls, d: Dict[str, Any]):
        missing_keys = set(["_type", "id", "label"]) - d.keys()
        if missing_keys:
            raise Exception(f"Missing keys {missing_keys} from definition {d}")

        if d["_type"] != cls.TYPE:
            raise TypeError(
                f"Cannot create item class of type '{cls.TYPE}' using definition: {d}"
            )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        cls.validate_definition(d)
        return cls(id=d["id"], label=d["label"])

    def to_dict(self) -> dict:
        return {
            "_type": self.__class__.TYPE,
            "id": self.id,
            "label": self.label,
        }

    def get_craft_cost(self, amount: int) -> Tuple[Dict[BaseItem, int], int]:
        """To be implemented by subclasses. Retrieves the crafting cost for this item.

        :param amount: The amount of this item that needs to be crafted

        :returns: A dictionary with <k,v> pair <BaseItem, int> and an integer. The dictionary
            contains a map of the different items and the corresponding amounts required in the craft.
            The integer indicates any excess of this item that was crafted, or -1 to indicate there is
            nothing further to craft and the returned crafting cost should not be further processed
        """
        raise NotImplementedError()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseItem):
            return self.id == other.id
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"<{self.label} - {self.id}>"
