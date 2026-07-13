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
    def test_init_and_validate_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)

            inventory, recipes, inspiration = KITCHEN.load_and_validate(kitchen)

            self.assertEqual(inventory["items"], [])
            self.assertEqual(recipes["recipes"], [])
            self.assertEqual(inspiration["ideas"], [])

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
            inventory_path = kitchen / "inventory.json"
            recipes_path = kitchen / "recipes.json"
            inventory = json.loads(inventory_path.read_text())
            inventory["items"] = [
                {
                    "id": "spinach",
                    "name": "Baby Spinach",
                    "quantity": 5,
                    "unit": "oz",
                    "category": "produce",
                    "location": "fridge",
                    "expires_on": (date.today() + timedelta(days=2)).isoformat(),
                    "opened": True,
                    "notes": "",
                    "updated_at": "2026-07-12T15:00:00Z",
                }
            ]
            inventory_path.write_text(json.dumps(inventory))
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

    def test_validation_rejects_missing_required_inventory_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kitchen = Path(directory) / "kitchen"
            KITCHEN.initialize(kitchen, force=False)
            inventory_path = kitchen / "inventory.json"
            inventory = json.loads(inventory_path.read_text())
            inventory["items"] = [{}]
            inventory_path.write_text(json.dumps(inventory))

            with self.assertRaisesRegex(KITCHEN.KitchenError, "is missing"):
                KITCHEN.load_and_validate(kitchen)


if __name__ == "__main__":
    unittest.main()
