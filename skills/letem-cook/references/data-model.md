# Kitchen memory model

Let Em Cook uses two Markdown memory files and two structured JSON stores. Dates use `YYYY-MM-DD`; timestamps use ISO 8601 UTC.

## `inventory.md`

Treat this as the canonical current ingredient memory. Keep the heading, `Last updated` line, table header, and column order intact so the CLI can validate and summarize it.

```markdown
# Ingredient Inventory

Last updated: 2026-07-12T15:00:00Z

| ID | Ingredient | Quantity | Unit | Category | Location | Use by | Opened | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baby-spinach-2026-07-12 | baby spinach | 5 | oz | produce | fridge | 2026-07-15 | yes |  |
```

Use `unknown` for an unknown quantity, use-by date, or opened state. Use `yes`, `no`, or `unknown` for `Opened`. Use separate rows for batches with different use-by dates. Do not put the pipe character in cell values.

## `cooking-log.md`

Use this file for the post-cooking reconciliation loop. `Pending inventory check` contains meals that still require a leftover check. `Cooked meals` preserves dated outcomes and the inventory changes confirmed by the user.

```markdown
# Cooking Log

## Pending inventory check

- 2026-07-12 — Spinach white bean pasta

## Cooked meals

### 2026-07-12 — Spinach white bean pasta

- Outcome: Good; wanted more acidity.
- Inventory update: 2 oz baby spinach remains; opened pasta removed.
- Recipe update: Rated 4/5.
```

Use `None.` when a section has no entries. Do not clear a pending check until the user answers what remains.

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

Use `idea`, `testing`, or `promoted` for `status`.
