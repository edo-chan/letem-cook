# Kitchen data model

Let Em Cook uses three JSON files. Keep `schema_version` at `1` until a migration is intentionally designed. Dates use `YYYY-MM-DD`; timestamps use ISO 8601 UTC.

## `inventory.json`

```json
{
  "schema_version": 1,
  "updated_at": null,
  "items": [
    {
      "id": "baby-spinach-2026-07-12",
      "name": "baby spinach",
      "quantity": 5,
      "unit": "oz",
      "category": "produce",
      "location": "fridge",
      "expires_on": "2026-07-15",
      "opened": true,
      "notes": "",
      "updated_at": "2026-07-12T15:00:00Z"
    }
  ]
}
```

`quantity` may be a number or `null`. `expires_on` may be a date or `null`. Use separate item records for batches with different expiration dates.

## `recipes.json`

```json
{
  "schema_version": 1,
  "recipes": [
    {
      "id": "spinach-white-bean-pasta",
      "name": "Spinach white bean pasta",
      "servings": 4,
      "tags": ["weeknight", "vegetarian"],
      "ingredients": [
        {
          "name": "baby spinach",
          "quantity": 5,
          "unit": "oz",
          "optional": false,
          "substitutions": ["kale"]
        }
      ],
      "steps": ["Cook the pasta."],
      "notes": "",
      "source": null,
      "last_cooked": null,
      "rating": null
    }
  ]
}
```

`servings` is a positive number. `rating` may be `null` or a number from 1 through 5. `source` may be a URL, book citation, person, or `null`.

## `inspiration.json`

```json
{
  "schema_version": 1,
  "ideas": [
    {
      "id": "crispy-bean-spinach-bowls",
      "title": "Crispy bean and spinach bowls",
      "prompt": "Use the spinach soon and build around pantry beans.",
      "tags": ["weeknight", "vegetarian"],
      "anchor_ingredients": ["baby spinach", "white beans"],
      "status": "idea",
      "variations": ["Add a fried egg", "Turn it into a warm pita filling"],
      "notes": "Needs a sauce before promotion to a recipe.",
      "created_at": "2026-07-12T15:00:00Z"
    }
  ]
}
```

Use `idea`, `testing`, or `promoted` for `status`. A promoted idea should point to the resulting recipe in `notes` until the schema gains an explicit relationship.
