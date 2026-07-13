---
name: letem-cook
description: Manage a local home kitchen system that connects ingredient inventory and expiration tracking, a personal recipe library, recipe inspiration, substitutions, and variations. Use when a user wants to record groceries or pantry changes, decide what to cook from ingredients on hand, reduce food waste, save or adapt recipes, plan meals, brainstorm dishes, or initialize and maintain the Let Em Cook JSON workspace.
---

# Let Em Cook

Operate a local-first home-chef system. Treat the user's kitchen files as the source of truth, preserve uncertainty, and turn available ingredients into realistic cooking options.

## Start or locate the kitchen

Look for `inventory.json`, `recipes.json`, and `inspiration.json` in the user's chosen kitchen directory. If no workspace exists, initialize one with:

```bash
python3 <skill-directory>/scripts/kitchen.py init <kitchen-directory>
```

Do not overwrite an existing workspace unless the user explicitly asks. Read [references/data-model.md](references/data-model.md) before directly editing kitchen records.

Validate after modifying JSON:

```bash
python3 <skill-directory>/scripts/kitchen.py validate <kitchen-directory>
```

## Maintain ingredient inventory

- Record only quantities, dates, locations, and states the user supplied or confirmed.
- Use `null` for an unknown quantity or expiration date; never convert uncertainty into a guessed value.
- Keep one stable item ID per separately tracked package or batch when expiration dates differ.
- Update `updated_at` whenever an item changes.
- Reduce or remove quantities only after the user reports consumption, disposal, or correction.
- Flag expired food and uncertain food safety; do not recommend questionable ingredients merely to avoid waste.

Use the status command to surface inventory totals and near-term expirations:

```bash
python3 <skill-directory>/scripts/kitchen.py status <kitchen-directory> --days 7
```

## Maintain recipes

- Preserve the original recipe and source when known.
- Store required and optional ingredients separately through each ingredient's `optional` field.
- Keep instructions executable: ordered steps, expected servings, and important timing or equipment notes.
- Use stable recipe IDs so later ratings, cook history, and variations can refer to the same recipe.
- Record substitutions only when they are plausible; state likely changes to flavor, texture, cook time, or yield.

## Find what to cook

Rank options using this order:

1. dietary restrictions and allergen safety
2. ingredients that are expired or unsafe to use are excluded
3. user constraints such as time, equipment, effort, and servings
4. recipes that use ingredients expiring soon
5. pantry coverage and number of missing required ingredients
6. user preferences, ratings, and variety from recent meals

Run deterministic pantry matching as a starting point:

```bash
python3 <skill-directory>/scripts/kitchen.py match <kitchen-directory> --top 5 --days 7
```

Treat name-based matches as candidates, not proof that quantities are sufficient. Check quantities and units before presenting a recipe as fully cookable.

For each recommendation, report:

- why it fits now
- ingredients on hand that it uses, especially expiring items
- required ingredients that are missing or uncertain
- realistic time, equipment, or skill constraints when known
- one useful variation, if it adds value

## Capture inspiration

Use inspiration records for promising ideas that are not yet complete recipes. Base ideas on some combination of expiring ingredients, complementary pantry staples, seasonal themes, cuisines, techniques, leftovers, or user cravings.

Keep an inspiration item concise. Include anchor ingredients, tags, status, notes, and candidate variations. Promote it to `recipes.json` only after there is enough detail to cook it repeatably.

## Create variations

Label the kind of change:

- **substitution**: replace an ingredient and explain the tradeoff
- **dietary adaptation**: satisfy a stated restriction without claiming allergen safety when cross-contact or labels are unknown
- **technique variation**: change the cooking method
- **format variation**: reuse the flavor profile as a bowl, soup, sandwich, pasta, salad, or similar form
- **scale variation**: adjust servings while calling out ingredients or timings that do not scale linearly

Preserve the recipe's identity. Prefer one to three deliberate changes over an unbounded list of swaps.

## Apply safety boundaries

- Ask about dietary restrictions or allergies when they materially affect recommendations and are not known.
- Never infer allergen-free status from an ingredient name alone.
- Do not treat an expiration date as the sole food-safety test. Call out uncertainty around storage history, spoilage, raw animal products, and leftovers.
- Distinguish food-safety guidance from taste or quality advice.
- Use authoritative local guidance for exact safe temperatures or storage windows when high-stakes food-safety advice is requested.
