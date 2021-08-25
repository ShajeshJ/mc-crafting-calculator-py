from dataclasses import dataclass
from models.items.base_item import BaseItem
from typing import Dict, ItemsView, List, Tuple
from libraries.items import ITEM_RECIPES, get_item
from collections import OrderedDict
from tabulate import tabulate


@dataclass
class CraftResult:
    excess_items: Dict[BaseItem, int]
    craft_steps: OrderedDict[BaseItem, int]
    raw_item_costs: Dict[BaseItem, int]


def run():
    crafting_stack: List[Tuple[BaseItem, int]] = []

    while True:
        next_item = input("Next to craft? ")
        if next_item:
            try:
                crafting_stack.append(query_item(next_item))
                print("")
            except StopIteration:
                print("\nInvalid item id. Try again...")
                continue
        else:
            break

    craft_results = craft_items(crafting_stack)

    print("\nCrafting Costs:")
    print("---------------")
    pprint_data(
        craft_results.raw_item_costs.items(),
        headers=["Raw Item", "Amount", "Amount in Stacks"],
    )

    print("\n---------------")

    print("\nCraft Steps:")
    print("------------")
    pprint_data(
        craft_results.craft_steps.items(),
        headers=["Item To Craft", "Amount", "Amount in Stacks"],
    )

    print("\n---------------")

    print("\nExcess Items:")
    print("-------------")
    pprint_data(
        craft_results.excess_items.items(),
        headers=["Excess Item", "Amount", "Amount in Stacks"],
    )


def query_item(item_id: str):
    item = get_item(item_id)
    amt = int(input(f"How many {item.label} do you want to craft? "))
    return item, amt


def craft_items(crafting_stack: List[Tuple[BaseItem, int]]):
    excess_items: Dict[BaseItem, int] = {}
    craft_steps: OrderedDict[BaseItem, int] = OrderedDict()
    raw_costs: Dict[BaseItem, int] = {}

    while crafting_stack:
        next_to_craft, req_amt = crafting_stack.pop()

        # Fulfill the required amount for the next craft by taking as much off
        # the excess pile as possible
        current_excess = excess_items.get(next_to_craft, 0)
        excess_amt_to_take = min(req_amt, current_excess)
        excess_items[next_to_craft] = current_excess - excess_amt_to_take
        req_amt = req_amt - excess_amt_to_take

        craft_cost, excess_made = next_to_craft.get_craft_cost(req_amt)

        if excess_made == -1:
            # Base Case; crafted items should not be further processed, and should instead
            # be added to the final results
            for item, amt in craft_cost.items():
                raw_costs[item] = raw_costs.get(item, 0) + amt
        else:
            excess_items[next_to_craft] = excess_items[next_to_craft] + excess_made
            crafting_stack.extend(craft_cost.items())
            craft_steps[next_to_craft] = (
                craft_steps.get(next_to_craft, 0) + req_amt + excess_made
            )
            craft_steps.move_to_end(key=next_to_craft, last=False)

    excess_items = {k: v for k, v in excess_items.items() if v > 0}

    return CraftResult(
        excess_items=excess_items,
        craft_steps=craft_steps,
        raw_item_costs=raw_costs,
    )


def pprint_data(data: ItemsView[BaseItem, int], headers: List[str]):
    print(
        tabulate(
            map(lambda r: (r[0].label, r[1], f"{r[1]//64} stacks + {r[1]%64}"), data),
            headers=headers,
        )
    )
