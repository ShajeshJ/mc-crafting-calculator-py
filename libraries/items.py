import pkgutil
import importlib
import importlib.resources
import json
from typing import Dict, List, Type

import models.items as items_module
import recipes

from models.items.base_item import BaseItem
from models.items.craftable_item import CraftableItem


ITEM_CLASSES: Dict[str, Type[BaseItem]] = {}
ITEM_RECIPES: List[BaseItem] = []


def get_item(item_id: str):
    return next(filter(lambda x: x.id == item_id, ITEM_RECIPES))


def reload_item_classes():
    """Small helper function to load `ITEM_CLASSES` with all
    classes that subclass :py:func:`BaseItem <models.items.base_item.BaseItem>`
    """
    global ITEM_CLASSES
    ITEM_CLASSES = {}

    # Just blindly importing all modules in the items subfolder, to ensure
    # `BaseItem.__subclasses__` is loaded correctly
    mods = pkgutil.iter_modules(items_module.__path__, f"{items_module.__package__}.")
    for mod in mods:
        importlib.import_module(mod.name)

    for item_cls in BaseItem.__subclasses__():
        if (
            item_cls.TYPE is None
            or not isinstance(item_cls.TYPE, str)
            or item_cls.TYPE in ITEM_CLASSES
        ):
            raise Exception(
                f"{item_cls.__name__} must implement static class attribute 'TYPE' with a unique string value"
            )

        ITEM_CLASSES[item_cls.TYPE] = item_cls


def reload_item_recipes():
    """Small helper function to load `ITEM_RECIPES` with all
    JSON item recipes defined in the `recipe_data` folder"""

    reload_item_classes()
    global ITEM_RECIPES
    ITEM_RECIPES = []
    temp_recipe_map: Dict[str, BaseItem] = {}

    for recipe_file in importlib.resources.contents(recipes):
        if not recipe_file.endswith(".json"):
            continue

        recipe_data = json.loads(importlib.resources.read_text(recipes, recipe_file))
        if not isinstance(recipe_data, dict):
            raise TypeError(
                f"Expected recipe data to be a JSON object. Instead received: {recipe_data}"
            )

        if recipe_data.get("_type") not in ITEM_CLASSES:
            raise TypeError(
                f"Unknown item class type from recipe definition: {recipe_data}"
            )

        item_recipe = ITEM_CLASSES[recipe_data["_type"]].from_dict(recipe_data)

        if item_recipe.id in temp_recipe_map:
            raise Exception(f"Duplicate entry for item id {item_recipe.id}")

        ITEM_RECIPES.append(item_recipe)
        temp_recipe_map[item_recipe.id] = item_recipe

    for item in ITEM_RECIPES:
        if isinstance(item, CraftableItem):
            item.build_craft_costs(temp_recipe_map)


reload_item_recipes()
