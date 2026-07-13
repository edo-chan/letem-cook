from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "letem-cook" / "scripts" / "kitchen.py"
EXAMPLE = ROOT / "skills" / "letem-cook" / "examples" / "ed-kitchen"
SPEC = importlib.util.spec_from_file_location("kitchen", SCRIPT)
assert SPEC and SPEC.loader
KITCHEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KITCHEN)


class KitchenTest(unittest.TestCase):
    def test_bundled_example_uses_confirmed_inventory_without_guessing(self) -> None:
        inventory, pantry, recipes, inspiration, cooking_log, profile, people = (
            KITCHEN.load_and_validate(EXAMPLE)
        )
        by_name = {item["name"]: item for item in inventory}

        self.assertEqual(len(inventory), 5)
        self.assertEqual(by_name["T-bone steak"]["quantity"], "0.5")
        self.assertEqual(by_name["Croissants"]["quantity"], "4")
        self.assertEqual(by_name["Alpaca chicken"]["quantity"], "2")
        self.assertEqual(by_name["Cooked rice"]["unit"], "bento box")
        self.assertEqual(by_name["Dim sum"]["location"], "fridge")
        self.assertEqual(by_name["Dim sum"]["use_by"], "unknown")
        self.assertEqual(KITCHEN.ready_leftovers(inventory), [])
        self.assertEqual(len(KITCHEN.leftovers_needing_review(inventory)), 4)
        self.assertEqual(len(pantry), 1)
        self.assertEqual(pantry[0]["name"], "Miso")
        self.assertEqual(pantry[0]["category"], "condiments")
        self.assertIn("T-bone steak", cooking_log)
        self.assertEqual(profile["Usual meal size"], "unknown")
        self.assertEqual(people, {})
        self.assertEqual(recipes["recipes"], [])
        self.assertEqual(inspiration["ideas"], [])

    def test_commands_default_to_persistent_memory_directory(self) -> None:
        args = KITCHEN.build_parser().parse_args(["status"])

        self.assertEqual(args.kitchen, KITCHEN.default_kitchen())

    def test_init_and_validate_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)

            inventory, pantry, recipes, inspiration, cooking_log, profile, people = (
                KITCHEN.load_and_validate(kitchen)
            )

            self.assertEqual(inventory, [])
            self.assertEqual(pantry, [])
            self.assertEqual(recipes["recipes"], [])
            self.assertEqual(inspiration["ideas"], [])
            self.assertIn("## Pending inventory check", cooking_log)
            self.assertEqual(profile["Usual meal size"], "unknown")
            self.assertEqual(people, {})

    def test_people_flavor_profile_parses_all_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            (kitchen / "people.md").write_text(
                "# People Flavor Profiles\n\n"
                "Last updated: 2026-07-12T15:00:00Z\n\n"
                "## People\n\n"
                "### Alex\n\n"
                "- Relationship: friend\n"
                "- Likes: citrus\n"
                "- Dislikes: overly sweet sauces\n"
                "- Salt preference: medium\n"
                "- Sweetness preference: low\n"
                "- Acidity preference: bright\n"
                "- Bitterness preference: unknown\n"
                "- Umami preference: high\n"
                "- Heat preference: hot\n"
                "- Richness preference: medium\n"
                "- Aromatic preferences: garlic\n"
                "- Texture preferences: crisp\n"
                "- Doneness preferences: medium-rare steak\n"
                "- Preferred cuisines: Korean\n"
                "- Dietary restrictions: none stated\n"
                "- Allergies: none stated\n"
                "- Evidence: 2 meal feedback entries\n"
                "- Last feedback: 2026-07-12\n"
            )

            *_, people = KITCHEN.load_and_validate(kitchen)

            self.assertEqual(people["Alex"]["Heat preference"], "hot")
            self.assertEqual(people["Alex"]["Evidence"], "2 meal feedback entries")

    def test_init_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)

            with self.assertRaisesRegex(KITCHEN.KitchenError, "refusing to overwrite"):
                KITCHEN.initialize(kitchen, force=False)

    def test_match_reports_coverage_and_expiring_ingredients(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            inventory_path = kitchen / "inventory.md"
            recipes_path = kitchen / "recipes.json"
            inventory_path.write_text(
                "# Ingredient Inventory\n\n"
                "Last updated: 2026-07-12T15:00:00Z\n\n"
                f"{KITCHEN.INVENTORY_HEADER}\n"
                f"{KITCHEN.INVENTORY_SEPARATOR}\n"
                "| spinach | Baby Spinach | 5 | oz | produce | fridge | "
                f"{(date.today() + timedelta(days=2)).isoformat()} | yes | |\n"
            )
            recipes = json.loads(recipes_path.read_text())
            recipes["recipes"] = [
                {
                    "id": "spinach-pasta",
                    "name": "Spinach pasta",
                    "servings": 2,
                    "tags": ["weeknight"],
                    "ingredients": [
                        {
                            "name": "baby spinach",
                            "quantity": 5,
                            "unit": "oz",
                            "optional": False,
                            "substitutions": [],
                        },
                        {
                            "name": "pasta",
                            "quantity": 8,
                            "unit": "oz",
                            "optional": False,
                            "substitutions": [],
                        },
                    ],
                    "steps": ["Cook it."],
                    "notes": "",
                    "source": None,
                    "last_cooked": None,
                    "rating": None,
                }
            ]
            recipes_path.write_text(json.dumps(recipes))

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "match", str(kitchen)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("50% pantry coverage", result.stdout)
            self.assertIn("Missing: pasta", result.stdout)
            self.assertIn("Expiring soon: baby spinach", result.stdout)

    def test_match_prioritizes_ready_leftovers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            inventory_path = kitchen / "inventory.md"
            inventory_path.write_text(
                "# Ingredient Inventory\n\n"
                "Last updated: 2026-07-12T15:00:00Z\n\n"
                f"{KITCHEN.INVENTORY_HEADER}\n"
                f"{KITCHEN.INVENTORY_SEPARATOR}\n"
                "| chili-leftover | Bean chili | 2 | portions | leftover | fridge | "
                f"{(date.today() + timedelta(days=2)).isoformat()} | yes | Cooked yesterday. |\n"
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "match", str(kitchen)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Eat leftovers first:", result.stdout)
            self.assertIn("Bean chili (2 portions", result.stdout)
            self.assertLess(
                result.stdout.index("Eat leftovers first:"),
                result.stdout.index("No saved recipes"),
            )

    def test_match_uses_food_pantry_but_excludes_medicine(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            pantry_path = kitchen / "pantry.md"
            pantry_path.write_text(
                "# Agentic Pantry\n\n"
                "Last updated: 2026-07-12T15:00:00Z\n\n"
                "## Categories\n\n"
                + "".join(f"- {category}\n" for category in KITCHEN.PANTRY_CATEGORIES)
                + "\n## Items\n\n"
                f"{KITCHEN.PANTRY_HEADER}\n"
                f"{KITCHEN.INVENTORY_SEPARATOR}\n"
                "| ramen | Instant ramen | 2 | packs | ramen | pantry | unknown | no | |\n"
                "| medicine | Cold medicine | 1 | box | medicine | pantry | unknown | yes | |\n"
            )
            recipes_path = kitchen / "recipes.json"
            recipes = json.loads(recipes_path.read_text())
            recipes["recipes"] = [
                {
                    "id": "ramen-test",
                    "name": "Ramen test",
                    "servings": 1,
                    "tags": [],
                    "ingredients": [
                        {
                            "name": "instant ramen",
                            "quantity": 1,
                            "unit": "pack",
                            "optional": False,
                            "substitutions": [],
                        },
                        {
                            "name": "cold medicine",
                            "quantity": 1,
                            "unit": "box",
                            "optional": False,
                            "substitutions": [],
                        },
                    ],
                    "steps": ["Test matching only."],
                    "notes": "",
                    "source": None,
                    "last_cooked": None,
                    "rating": None,
                }
            ]
            recipes_path.write_text(json.dumps(recipes))

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "match", str(kitchen)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("50% pantry coverage", result.stdout)
            self.assertIn("Missing: cold medicine", result.stdout)

    def test_status_reports_agentic_pantry_category_breakdown(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "status", str(EXAMPLE)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Pantry items: 1", result.stdout)
        self.assertIn("condiments=1", result.stdout)
        self.assertIn("medicine=0", result.stdout)

    def test_leftover_without_use_by_date_is_not_presented_as_ready(self) -> None:
        inventory = [
            {
                "id": "unknown-leftover",
                "name": "Mystery leftovers",
                "quantity": "1",
                "unit": "portion",
                "category": "leftover",
                "location": "fridge",
                "use_by": "unknown",
                "opened": "yes",
                "notes": "",
            }
        ]

        self.assertEqual(KITCHEN.ready_leftovers(inventory), [])
        self.assertEqual(KITCHEN.leftovers_needing_review(inventory), inventory)

    def test_validation_rejects_malformed_inventory_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            inventory_path = kitchen / "inventory.md"
            inventory_path.write_text(
                "# Ingredient Inventory\n\n"
                "Last updated: 2026-07-12T15:00:00Z\n\n"
                f"{KITCHEN.INVENTORY_HEADER}\n"
                f"{KITCHEN.INVENTORY_SEPARATOR}\n"
                "| spinach | Baby Spinach | 5 | oz |\n"
            )

            with self.assertRaisesRegex(KITCHEN.KitchenError, "must have 9 columns"):
                KITCHEN.load_and_validate(kitchen)

    def test_skill_requires_post_cook_leftover_reconciliation(self) -> None:
        skill = (ROOT / "skills" / "letem-cook" / "SKILL.md").read_text()

        self.assertIn("Treat post-cook reconciliation as mandatory", skill)
        self.assertIn("Are there any ingredients left?", skill)
        self.assertIn("Wait for the answer before changing consumed quantities", skill)
        self.assertIn("leave the pending check in the log", skill)
        self.assertIn("safe prepared leftovers", skill)
        self.assertIn("usual meal size", skill)
        self.assertIn("whether each would make it again", skill)
        self.assertIn("Treat `profile.md` as the source of truth", skill)
        self.assertIn("Treat `people.md` as the source of truth", skill)
        self.assertIn("Feedback by person", skill)
        self.assertIn("Shared themes", skill)
        self.assertIn("Differences", skill)
        self.assertIn("Do not treat silence as approval", skill)
        self.assertIn("Act as an agentic kitchen", skill)
        self.assertIn("Maintain the agentic pantry", skill)
        self.assertIn("`pantry.md` as the only source of truth", skill)
        self.assertIn("pancake or cake mixes", skill)
        self.assertIn("Never treat medicine as a recipe ingredient", skill)


if __name__ == "__main__":
    unittest.main()
