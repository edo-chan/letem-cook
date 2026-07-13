# Kitchen memory model

Let Em Cook uses four Markdown memory files and two structured JSON stores. Dates use `YYYY-MM-DD`; timestamps use ISO 8601 UTC.

## `inventory.md`

Treat this as the canonical current ingredient memory. Keep the heading, `Last updated` line, table header, and column order intact so the CLI can validate and summarize it.

```markdown
# Ingredient Inventory

Last updated: 2026-07-12T15:00:00Z

| ID | Ingredient | Quantity | Unit | Category | Location | Use by | Opened | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baby-spinach-2026-07-12 | baby spinach | 5 | oz | produce | fridge | 2026-07-15 | yes |  |
| chili-leftover-2026-07-12 | bean chili | 2 | portions | leftover | fridge | 2026-07-15 | yes | Cooked 2026-07-12. |
```

Use `unknown` for an unknown quantity, use-by date, or opened state. Use `yes`, `no`, or `unknown` for `Opened`. Use separate rows for batches with different use-by dates. Use category `leftover` for prepared meal-ready food and prefer quantity unit `portions`. Do not put the pipe character in cell values.

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
- Feedback by person: Ed liked the texture but wanted more acidity; Sam liked the seasoning.
- Shared themes: 2 of 2 liked the texture.
- Differences: Ed wanted more acidity; Sam did not request a change.
- Next-time changes: Offer lemon at the table for Ed.
- Profile updates: Ed prefers brighter acidity, supported by repeated feedback.
```

Use `None.` when a section has no entries. Do not clear a pending check until the user answers what remains.

## `people.md`

Treat this as the source of truth for individual flavor profiles. Use one `###` section per person and keep all fields, writing `unknown` when evidence is absent.

```markdown
# People Flavor Profiles

Last updated: 2026-07-12T15:00:00Z

## People

### Ed

- Relationship: primary cook
- Likes: citrus, charred edges
- Dislikes: overly sweet savory dishes
- Salt preference: medium
- Sweetness preference: low in savory food
- Acidity preference: bright
- Bitterness preference: unknown
- Umami preference: high
- Heat preference: medium-hot
- Richness preference: medium
- Aromatic preferences: garlic, scallion
- Texture preferences: crisp vegetables
- Doneness preferences: medium-rare steak
- Preferred cuisines: Korean, Mexican, Italian
- Dietary restrictions: none stated
- Allergies: none stated
- Evidence: 3 meal feedback entries
- Last feedback: 2026-07-12
```

Keep meal-specific reactions in `cooking-log.md`. Update durable profile fields only from an explicit general statement or a pattern supported across meals. `Evidence` should say how many feedback entries currently support the synthesized profile.

## `profile.md`

Treat this as the source of truth for household-wide meal patterns and shared defaults. Keep person-specific flavor preferences in `people.md`, and keep unknown values explicit until the user supplies them.

```markdown
# Kitchen Profile

Last updated: 2026-07-12T15:00:00Z

## Meal pattern

- Usual meal size: 2 servings
- Usual diners: 2 adults
- Desired leftover portions: 1

## Preferences

- Likes: spicy food, citrus, crunchy textures
- Dislikes: overly sweet savory dishes
- Dietary restrictions: none stated
- Allergies: none stated
- Preferred cuisines: Korean, Mexican, Italian
- Spice level: hot
- Texture preferences: crisp vegetables
- Effort preference: 30-minute weeknight meals
- Leftover preference: eat leftovers before cooking a new meal
```

Record `unknown` rather than `none` when the user has not answered. Use `none stated` only after the user confirms no restriction or allergy. Keep one comma-separated line per field so the profile remains easy to scan and update.

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
