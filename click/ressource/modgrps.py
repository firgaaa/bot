import json
import copy


def init_qty(tree: list) -> None:
    """Met qty=0 sur tous les modifiers de l'arbre (muté en place). Comme v2 avant choose()."""
    if not tree:
        return
    for group in tree:
        for mod in group.get("modifiers", []):
            mod["qty"] = 0
            if mod.get("modgrps"):
                init_qty(mod["modgrps"])


def build_modgrps_from_tree(tree: list) -> list:
    """
    Construit la liste modgrps pour l'API KFC à partir de l'arbre déjà rempli (qty set).
    Même logique que v2 : [ build_modgrp(group) for group in tree ].
    """
    if not tree:
        return []
    return [build_modgrp(g) for g in tree]


def select_n(group: dict) -> int:
    """
    Function used to select the modifier when you can select more than 1, you may need to edit this or make your own selection system if its you're not using CLI.

    Args:
        group (dict): product's modgrps group. Refer to the doc

    Returns:
        selectedModifier (int): the chosen modifier index
    """
    print(f"\n=== {group['name']} ===")

    modifiers = group["modifiers"]

    for index, mod in enumerate(modifiers):
        print(f"{index + 1}. {mod['name']}")

    
    choice = []

    for i in range(group['max']):
        choice_i = int(input(f"Choix {i+1} : ")) - 1
        choice.append(choice_i)


    for mod in modifiers:
        mod["qty"] = 0

    
    for choice_i in choice:
        selected = modifiers[choice_i]
        selected["qty"] += 1

    return choice

def select_group(group: dict) -> int:
    """
    Function used to select the modifier, you may need to edit this or make your own selection system if its you're not using CLI.

    Args:
        group (dict): product's modgrps group. Refer to the doc

    Returns:
        selectedModifier (int): the chosen modifier index
    """
    print(f"\n=== {group['name']} ===")

    modifiers = group["modifiers"]

    for index, mod in enumerate(modifiers):
        print(f"{index + 1}. {mod['name']}")

    
    choice = int(input("Select option: ")) - 1

    for mod in modifiers:
        mod["qty"] = 0

    
    selected = modifiers[choice]
    selected["qty"] = group['max'] #Force it to max, you may want to change this if you don't want 3x the same sauce

    for nested_group in selected["modgrps"]: #Recursive devil
        choose(nested_group)

    return choice

def choose(group):
    """
    Just a little function used as a dispatcher

    Args:
        group (dict): product's modgrps group. Refer to the doc

    Returns:
        None
    """
    if group['max'] > 1:
        select_n(group)
    else:
        select_group(group)


def build_modifier(node):
    # Alignement v2: KFC peut renvoyer "price" ou "posPrice"
    unit_price = node.get("price") if node.get("price") is not None else node.get("posPrice", 0)
    if unit_price is None:
        unit_price = 0
    modifier = {
        "id": node["id"],
        "unitPrice": unit_price,
        "quantity": node.get("qty", 0),
    }

    if node.get("modgrps"):
        modifier["modgrps"] = [
            build_modgrp(mg) for mg in node["modgrps"]
        ]

    return modifier


def build_modgrp(group):
    return {
        "id": group["id"],
        "modifiers": [
            build_modifier(mod) for mod in group["modifiers"] if mod['qty'] > 0
        ]
    }



def ChooseModifications(modgrps: dict) -> dict:
    """
    Fonction designed to build the modgrps dict list associated to a product. More information in the doc

    Args:
        modgrps (dict): product's modgrps. Refer to the doc

    Returns:
        modgrpsInfo (dict list): a dict list containing information about the "modgrps" of a product. e.g : Beverage, Accompagnemet, Sauce and every "attributes" of a product
    """
    
    for group in modgrps:
        choose(group)

    return [
            build_modgrp(group) for group in modgrps
        ]