---
name: letem-cook
description: Manage a persistent local home-kitchen memory that connects Markdown ingredient and leftover inventory, cooking history, usual meal size, and food preferences with a personal recipe library, inspiration, substitutions, and variations. Use when a user wants to record groceries or pantry changes, prioritize prepared leftovers as a meal, cook from ingredients on hand, finish a cooking session and reconcile leftovers, remember household meal patterns or preferences, reduce food waste, save or adapt recipes, plan meals, brainstorm dishes, or initialize and maintain a Let Em Cook workspace.
---

# Let Em Cook

Operate a local-first home-chef system. Treat the kitchen workspace as durable memory, preserve uncertainty, and turn available ingredients into realistic cooking options.

## Load memory first

Resolve the kitchen workspace from `LETEM_COOK_HOME` when set; otherwise use `~/.letem-cook`. Treat that directory as actual persistent memory, not a disposable output. Before answering any inventory-dependent request, read:

- `inventory.md` for the canonical current ingredient inventory
- `cooking-log.md` for pending post-cook checks and recent outcomes
- `profile.md` for usual meal size, diners, constraints, and preferences
- `recipes.json` when saved recipes matter
- `inspiration.json` when ideas or variations matter

Do not rely on chat context as a substitute for these files. If `cooking-log.md` contains a pending inventory check, resolve it before making inventory-dependent recommendations.

If no workspace exists, initialize one with:

```bash
python3 <skill-directory>/scripts/kitchen.py init
```

Pass an explicit directory only when the user chooses a different memory location. Do not overwrite an existing workspace unless the user explicitly asks. Read [references/data-model.md](references/data-model.md) before directly editing memory. Validate after every memory update:

```bash
python3 <skill-directory>/scripts/kitchen.py validate
```

## Maintain ingredient memory

- Treat `inventory.md` as the only source of truth for current ingredients.
- Record only quantities, dates, locations, and states the user supplied or confirmed.
- Write `unknown` when a quantity, opened state, or use-by date is unknown; never guess.
- Keep one stable item ID per separately tracked package or batch when use-by dates differ.
- Update the `Last updated` timestamp whenever the inventory changes.
- Reduce or remove quantities only after the user reports consumption, disposal, or correction.
- Keep an exhausted item at quantity `0` only when its history is useful; otherwise remove its row.
- Add cooked leftovers as new inventory rows with category `leftover`, quantity measured in portions when possible, storage location, use-by date, and the source meal in notes.
- Flag expired food and uncertain food safety; do not recommend questionable ingredients merely to avoid waste.

Use the status command to surface inventory totals and near-term use-by dates:

```bash
python3 <skill-directory>/scripts/kitchen.py status <kitchen-directory> --days 7
```

## Complete every cooking session

Treat post-cook reconciliation as mandatory, not optional.

1. When cooking begins, add the meal under `Pending inventory check` in `cooking-log.md`.
2. After the final cooking step, or as soon as the user says they finished cooking, ask: **“Are there any ingredients left? If so, what is left and about how much? How many portions of the cooked meal are left?”**
3. Ask where prepared leftovers were stored and their use-by date when those facts are unknown. Also ask how the dish turned out and whether they would make it again when the user has not already said.
4. Wait for the answer before changing consumed quantities. Do not deduct the recipe's planned amounts automatically.
5. Update every affected row in `inventory.md`, including partial amounts, newly opened state, discarded food, and prepared leftovers. Record each prepared leftover as a meal-ready inventory row instead of only mentioning it in the cooking log.
6. Update `Last updated`, append the result under `Cooked meals`, and remove the matching pending check.
7. Update the saved recipe's `last_cooked`, rating, or notes only when the user supplied those facts.
8. Run validation and briefly confirm the memory changes.

If the user does not answer the leftover question, leave the pending check in the log and do not invent an inventory update. At the start of the next kitchen interaction, ask to resolve that pending check before claiming the inventory is current.

## Maintain meal size and preferences

- Treat `profile.md` as the source of truth for the user's usual meal size and durable preferences.
- If usual meal size is unknown, ask once before scaling a recipe or planning portions. Store the answer as servings and note the usual number of diners when supplied.
- Scale recipe recommendations to the usual meal size by default, then account for deliberately requested leftover portions.
- Record explicit likes, dislikes, dietary restrictions, allergies, cuisines, spice level, textures, effort, and leftover preferences.
- Keep recipe-specific feedback in the recipe or cooking log. Promote it to a general preference only when the user states it generally or a repeated pattern supports it.
- Never infer an allergy or dietary restriction from a dislike, nor erase an existing restriction without explicit confirmation.
- Update the profile timestamp whenever persistent preferences change.

## Maintain recipes

- Preserve the original recipe and source when known.
- Store required and optional ingredients separately through each ingredient's `optional` field.
- Keep instructions executable: ordered steps, expected servings, and important timing or equipment notes.
- Use stable recipe IDs so later ratings, cook history, and variations refer to the same recipe.
- Record substitutions only when they are plausible; state likely changes to flavor, texture, cook time, or yield.

## Find what to eat

Rank options using this order:

1. dietary restrictions and allergen safety
2. safe prepared leftovers, ordered by earliest known use-by date
3. expired or unsafe ingredients are excluded
4. user constraints such as time, equipment, effort, and usual meal size
5. ingredients that should be used soon
6. pantry coverage and missing required ingredients
7. user preferences, ratings, and variety from recent meals

Offer a safe leftover as the default next meal when it can cover the requested diners. If it is short on portions, suggest a simple side or combine compatible leftovers. Respect an explicit request to cook something new, but still mention leftovers that need attention soon. Never recommend a leftover as safe when storage history is unknown or questionable.

Run deterministic pantry matching as a starting point:

```bash
python3 <skill-directory>/scripts/kitchen.py match <kitchen-directory> --top 5 --days 7
```

The match command prints ready leftovers before recipe candidates. Treat name-based recipe matches as candidates, not proof that quantities are sufficient. Check quantities and units before presenting a recipe as fully cookable.

For each recommendation, report why it fits now, what it uses, what is missing or uncertain, relevant constraints, and one useful variation when it adds value.

## Capture inspiration and variations

Use inspiration records for promising ideas that are not yet complete recipes. Base them on ingredients to use soon, complementary staples, seasonal themes, cuisines, techniques, leftovers, or user cravings. Promote an idea to `recipes.json` only after it is repeatable.

Label recipe changes as a substitution, dietary adaptation, technique variation, format variation, or scale variation. Explain important tradeoffs and prefer one to three deliberate changes over an unbounded list of swaps.

## Apply safety boundaries

- Ask about dietary restrictions or allergies when they materially affect recommendations and are not known.
- Never infer allergen-free status from an ingredient name alone.
- Do not treat a use-by date as the sole food-safety test. Call out uncertainty around storage history, spoilage, raw animal products, and leftovers.
- Distinguish food-safety guidance from taste or quality advice.
- Use authoritative local guidance for exact safe temperatures or storage windows when high-stakes food-safety advice is requested.
