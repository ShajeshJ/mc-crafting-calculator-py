import json
import contextlib
from models.items.base_item import BaseItem
from models.items.craftable_item import CraftableItem
import os
from typing import Dict
from libraries.items import ITEM_RECIPES, get_item, reload_item_recipes
from models.items.raw_item import RawItem


def run():
    while True:
        item_id = input("\nID of item? ")
        try:
            get_item(item_id)
        except StopIteration:
            pass
        else:
            print("Item already exists. Try another ID")
            continue

        label = input("Label of item? ")

        print("\n1. Build Raw Item JSON")
        print("2. Build Craftable Item JSON")
        print("Anything else to quit")

        choice = input("Choice: ")

        if choice == "1":
            build_raw_recipe(item_id, label)
        elif choice == "2":
            build_craftable_recipe(item_id, label)
        else:
            break


def build_raw_recipe(item_id: str, label: str):
    save_item(RawItem(id=item_id, label=label))


def build_craftable_recipe(item_id: str, label: str):
    craft_amt = int(input("Amount per craft? "))
    craft_cost: Dict[str, int] = {}

    print("\nEnter items to include in the craft cost (enter empty to finish)")
    while True:
        craft_item_id = input("\nCraft Item ID? ")
        if craft_item_id:
            craft_cost[craft_item_id] = int(input("Craft Item Amount? "))
        else:
            break

    save_item(
        CraftableItem(
            id=item_id,
            label=label,
            craft_amt=craft_amt,
            raw_craft_costs=craft_cost,
        )
    )


def save_item(item: BaseItem):
    file_path = f"recipes/{item.id}.json"
    try:
        with open(file_path, "x") as fp:
            json.dump(item.to_dict(), fp, indent=4)
        reload_item_recipes()
    except:
        print("Malformed item. Deleting...")
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path)
