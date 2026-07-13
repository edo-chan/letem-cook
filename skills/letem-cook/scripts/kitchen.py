#!/usr/bin/env python3
"""Initialize, validate, summarize, and match a Let Em Cook kitchen."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


FILES = ("inventory.md", "cooking-log.md", "profile.md", "recipes.json", "inspiration.json")
INVENTORY_HEADER = (
    "| ID | Ingredient | Quantity | Unit | Category | Location | Use by | Opened | Notes |"
)
INVENTORY_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"


class KitchenError(ValueError):
    """Raised when kitchen data is missing or invalid."""


def default_kitchen() -> Path:
    return Path(os.environ.get("LETEM_COOK_HOME", "~/.letem-cook")).expanduser()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise KitchenError(f"missing {path}") from error
    except json.JSONDecodeError as error:
        raise KitchenError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise KitchenError(f"{path} must contain a JSON object")
    return value


def require_fields(record: dict[str, Any], fields: tuple[str, ...], context: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise KitchenError(f"{context} is missing: {', '.join(missing)}")


def require_type(value: Any, expected: type | tuple[type, ...], context: str) -> None:
    if not isinstance(value, expected):
        raise KitchenError(f"{context} has the wrong type")


def parse_date(value: Any, context: str) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise KitchenError(f"{context} must be a YYYY-MM-DD string or null")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise KitchenError(f"{context} must use YYYY-MM-DD") from error


def load_inventory(path: Path) -> list[dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise KitchenError(f"missing {path}") from error
    if not lines or lines[0] != "# Ingredient Inventory":
        raise KitchenError(f"{path} must start with '# Ingredient Inventory'")
    if not any(line.startswith("Last updated: ") for line in lines):
        raise KitchenError(f"{path} is missing the Last updated line")
    try:
        header_index = lines.index(INVENTORY_HEADER)
    except ValueError as error:
        raise KitchenError(f"{path} is missing the inventory table header") from error
    if header_index + 1 >= len(lines) or lines[header_index + 1] != INVENTORY_SEPARATOR:
        raise KitchenError(f"{path} has an invalid inventory table separator")

    items: list[dict[str, str]] = []
    ids: set[str] = set()
    fields = (
        "id",
        "name",
        "quantity",
        "unit",
        "category",
        "location",
        "use_by",
        "opened",
        "notes",
    )
    for line_number, line in enumerate(lines[header_index + 2 :], start=header_index + 3):
        if not line.startswith("|"):
            break
        values = [value.strip() for value in line.strip().strip("|").split("|")]
        if len(values) != len(fields):
            raise KitchenError(f"inventory.md line {line_number} must have {len(fields)} columns")
        item = dict(zip(fields, values, strict=True))
        context = f"inventory.md line {line_number}"
        if not item["id"] or item["id"] in ids:
            raise KitchenError(f"{context}.id must be non-empty and unique")
        if not item["name"]:
            raise KitchenError(f"{context}.name must be non-empty")
        ids.add(item["id"])
        if not item["quantity"]:
            raise KitchenError(f"{context}.quantity must be a value or 'unknown'")
        if item["opened"].casefold() not in {"yes", "no", "unknown"}:
            raise KitchenError(f"{context}.opened must be yes, no, or unknown")
        if item["use_by"].casefold() != "unknown":
            parse_date(item["use_by"], f"{context}.use_by")
        items.append(item)
    return items


def validate_cooking_log(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise KitchenError(f"missing {path}") from error
    required = ("# Cooking Log", "## Pending inventory check", "## Cooked meals")
    for heading in required:
        if heading not in content:
            raise KitchenError(f"{path} is missing '{heading}'")
    return content


def load_profile(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise KitchenError(f"missing {path}") from error
    required_headings = ("# Kitchen Profile", "## Meal pattern", "## Preferences")
    for heading in required_headings:
        if heading not in content:
            raise KitchenError(f"{path} is missing '{heading}'")
    required_fields = (
        "Usual meal size",
        "Usual diners",
        "Desired leftover portions",
        "Likes",
        "Dislikes",
        "Dietary restrictions",
        "Allergies",
        "Preferred cuisines",
        "Spice level",
        "Texture preferences",
        "Effort preference",
        "Leftover preference",
    )
    values: dict[str, str] = {}
    for line in content.splitlines():
        if not line.startswith("- ") or ":" not in line:
            continue
        name, value = line[2:].split(":", maxsplit=1)
        values[name.strip()] = value.strip()
    missing = [field for field in required_fields if not values.get(field)]
    if missing:
        raise KitchenError(f"{path} is missing profile values: {', '.join(missing)}")
    return values


def validate_recipes(data: dict[str, Any]) -> None:
    require_fields(data, ("schema_version", "recipes"), "recipes")
    if data["schema_version"] != 1:
        raise KitchenError("recipes schema_version must be 1")
    require_type(data["recipes"], list, "recipes.recipes")
    ids: set[str] = set()
    fields = (
        "id",
        "name",
        "servings",
        "tags",
        "ingredients",
        "steps",
        "notes",
        "source",
        "last_cooked",
        "rating",
    )
    ingredient_fields = ("name", "quantity", "unit", "optional", "substitutions")
    for index, recipe in enumerate(data["recipes"]):
        context = f"recipes.recipes[{index}]"
        require_type(recipe, dict, context)
        require_fields(recipe, fields, context)
        for field in ("id", "name", "notes"):
            require_type(recipe[field], str, f"{context}.{field}")
        if not recipe["id"] or recipe["id"] in ids:
            raise KitchenError(f"{context}.id must be non-empty and unique")
        ids.add(recipe["id"])
        require_type(recipe["servings"], (int, float), f"{context}.servings")
        if recipe["servings"] <= 0:
            raise KitchenError(f"{context}.servings must be positive")
        for field in ("tags", "ingredients", "steps"):
            require_type(recipe[field], list, f"{context}.{field}")
        for ingredient_index, ingredient in enumerate(recipe["ingredients"]):
            ingredient_context = f"{context}.ingredients[{ingredient_index}]"
            require_type(ingredient, dict, ingredient_context)
            require_fields(ingredient, ingredient_fields, ingredient_context)
            require_type(ingredient["name"], str, f"{ingredient_context}.name")
            require_type(ingredient["unit"], str, f"{ingredient_context}.unit")
            require_type(ingredient["optional"], bool, f"{ingredient_context}.optional")
            require_type(ingredient["substitutions"], list, f"{ingredient_context}.substitutions")
        if recipe["rating"] is not None:
            require_type(recipe["rating"], (int, float), f"{context}.rating")
            if not 1 <= recipe["rating"] <= 5:
                raise KitchenError(f"{context}.rating must be between 1 and 5")
        parse_date(recipe["last_cooked"], f"{context}.last_cooked")


def validate_inspiration(data: dict[str, Any]) -> None:
    require_fields(data, ("schema_version", "ideas"), "inspiration")
    if data["schema_version"] != 1:
        raise KitchenError("inspiration schema_version must be 1")
    require_type(data["ideas"], list, "inspiration.ideas")
    ids: set[str] = set()
    fields = (
        "id",
        "title",
        "prompt",
        "tags",
        "anchor_ingredients",
        "status",
        "variations",
        "notes",
        "created_at",
    )
    for index, idea in enumerate(data["ideas"]):
        context = f"inspiration.ideas[{index}]"
        require_type(idea, dict, context)
        require_fields(idea, fields, context)
        for field in ("id", "title", "prompt", "status", "notes", "created_at"):
            require_type(idea[field], str, f"{context}.{field}")
        if not idea["id"] or idea["id"] in ids:
            raise KitchenError(f"{context}.id must be non-empty and unique")
        ids.add(idea["id"])
        if idea["status"] not in {"idea", "testing", "promoted"}:
            raise KitchenError(f"{context}.status must be idea, testing, or promoted")
        for field in ("tags", "anchor_ingredients", "variations"):
            require_type(idea[field], list, f"{context}.{field}")


def load_and_validate(
    kitchen: Path,
) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any], str, dict[str, str]]:
    inventory = load_inventory(kitchen / "inventory.md")
    cooking_log = validate_cooking_log(kitchen / "cooking-log.md")
    profile = load_profile(kitchen / "profile.md")
    recipes = load_json(kitchen / "recipes.json")
    inspiration = load_json(kitchen / "inspiration.json")
    validate_recipes(recipes)
    validate_inspiration(inspiration)
    return inventory, recipes, inspiration, cooking_log, profile


def initialize(kitchen: Path, force: bool) -> None:
    template = Path(__file__).resolve().parent.parent / "assets" / "kitchen-template"
    kitchen.mkdir(parents=True, exist_ok=True)
    collisions = [name for name in FILES if (kitchen / name).exists()]
    if collisions and not force:
        raise KitchenError(f"refusing to overwrite: {', '.join(collisions)}")
    for name in FILES:
        shutil.copyfile(template / name, kitchen / name)
    print(f"Initialized kitchen at {kitchen}")


def expiring_items(inventory: list[dict[str, str]], days: int) -> list[dict[str, str]]:
    cutoff = date.today() + timedelta(days=days)
    matches = []
    for item in inventory:
        if item["use_by"].casefold() == "unknown":
            continue
        expires_on = parse_date(item["use_by"], f"inventory item {item['id']}.use_by")
        if expires_on is not None and expires_on <= cutoff and quantity_is_available(item["quantity"]):
            matches.append(item)
    return sorted(matches, key=lambda item: item["use_by"])


def quantity_is_available(quantity: str) -> bool:
    return quantity.casefold().strip() not in {"0", "0.0", "none", "empty"}


def ready_leftovers(inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    today = date.today()
    leftovers = []
    for item in inventory:
        if item["category"].casefold() != "leftover" or not quantity_is_available(item["quantity"]):
            continue
        if item["use_by"].casefold() == "unknown":
            continue
        use_by = parse_date(item["use_by"], f"leftover {item['id']}.use_by")
        if use_by is not None and use_by < today:
            continue
        leftovers.append(item)
    return sorted(
        leftovers,
        key=lambda item: (item["use_by"].casefold() == "unknown", item["use_by"], item["name"]),
    )


def show_leftovers(inventory: list[dict[str, str]]) -> None:
    leftovers = ready_leftovers(inventory)
    if not leftovers:
        return
    print("Eat leftovers first:")
    for item in leftovers:
        print(f"- {item['name']} ({item['quantity']} {item['unit']}, use by {item['use_by']})")


def leftovers_needing_review(inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        item
        for item in inventory
        if item["category"].casefold() == "leftover"
        and quantity_is_available(item["quantity"])
        and item["use_by"].casefold() == "unknown"
    ]


def show_status(kitchen: Path, days: int) -> None:
    inventory, recipes, inspiration, cooking_log, profile = load_and_validate(kitchen)
    expiring = expiring_items(inventory, days)
    leftovers = ready_leftovers(inventory)
    pending = "None." not in cooking_log.split("## Cooked meals", maxsplit=1)[0]
    print(f"Ingredients: {len(inventory)}")
    print(f"Recipes: {len(recipes['recipes'])}")
    print(f"Inspiration ideas: {len(inspiration['ideas'])}")
    print(f"Usual meal size: {profile['Usual meal size']}")
    print(f"Ready leftover meals: {len(leftovers)}")
    print(f"Leftovers needing date review: {len(leftovers_needing_review(inventory))}")
    print(f"Pending inventory check: {'yes' if pending else 'no'}")
    print(f"Expiring within {days} days: {len(expiring)}")
    for item in expiring:
        print(f"- {item['name']} ({item['use_by']}, {item['location']})")


def normalize_name(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def match_recipes(kitchen: Path, top: int, days: int) -> None:
    inventory, recipes, _, _, _ = load_and_validate(kitchen)
    show_leftovers(inventory)
    if ready_leftovers(inventory):
        print()
    available = {
        normalize_name(item["name"]): item
        for item in inventory
        if quantity_is_available(item["quantity"])
    }
    expiring = {normalize_name(item["name"]) for item in expiring_items(inventory, days)}
    ranked = []
    for recipe in recipes["recipes"]:
        required = [
            normalize_name(ingredient["name"])
            for ingredient in recipe["ingredients"]
            if not ingredient["optional"]
        ]
        matched = [name for name in required if name in available]
        missing = [name for name in required if name not in available]
        coverage = len(matched) / len(required) if required else 1.0
        expiring_matches = sorted(set(matched) & expiring)
        ranked.append((coverage, len(expiring_matches), recipe, missing, expiring_matches))
    ranked.sort(key=lambda result: (-result[0], -result[1], result[2]["name"].casefold()))
    if not ranked:
        print("No saved recipes yet.")
        return
    for coverage, _, recipe, missing, expiring_matches in ranked[:top]:
        print(f"{recipe['name']} — {coverage:.0%} pantry coverage")
        print(f"  Missing: {', '.join(missing) if missing else 'none by name'}")
        print(f"  Expiring soon: {', '.join(expiring_matches) if expiring_matches else 'none'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create an empty kitchen workspace")
    init_parser.add_argument("kitchen", nargs="?", type=Path, default=default_kitchen())
    init_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="validate all kitchen files")
    validate_parser.add_argument("kitchen", nargs="?", type=Path, default=default_kitchen())

    status_parser = subparsers.add_parser("status", help="summarize kitchen data")
    status_parser.add_argument("kitchen", nargs="?", type=Path, default=default_kitchen())
    status_parser.add_argument("--days", type=int, default=7)

    match_parser = subparsers.add_parser("match", help="rank recipes by ingredient-name coverage")
    match_parser.add_argument("kitchen", nargs="?", type=Path, default=default_kitchen())
    match_parser.add_argument("--top", type=int, default=5)
    match_parser.add_argument("--days", type=int, default=7)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            initialize(args.kitchen, args.force)
        elif args.command == "validate":
            load_and_validate(args.kitchen)
            print(f"Valid kitchen at {args.kitchen}")
        elif args.command == "status":
            if args.days < 0:
                raise KitchenError("--days cannot be negative")
            show_status(args.kitchen, args.days)
        elif args.command == "match":
            if args.top <= 0 or args.days < 0:
                raise KitchenError("--top must be positive and --days cannot be negative")
            match_recipes(args.kitchen, args.top, args.days)
    except KitchenError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
