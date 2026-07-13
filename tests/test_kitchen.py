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
SPEC = importlib.util.spec_from_file_location("kitchen", SCRIPT)
assert SPEC and SPEC.loader
KITCHEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KITCHEN)


class KitchenTest(unittest.TestCase):
    def test_commands_default_to_persistent_memory_directory(self) -> None:
        args = KITCHEN.build_parser().parse_args(["status"])

        self.assertEqual(args.kitchen, KITCHEN.default_kitchen())

    def test_init_and_validate_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)

            inventory, recipes, inspiration, cooking_log = KITCHEN.load_and_validate(kitchen)

            self.assertEqual(inventory, [])
            self.assertEqual(recipes["recipes"], [])
            self.assertEqual(inspiration["ideas"], [])
            self.assertIn("## Pending inventory check", cooking_log)

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


if __name__ == "__main__":
    unittest.main()
