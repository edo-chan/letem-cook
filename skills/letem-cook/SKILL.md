---
name: letem-cook
description: Run an agentic kitchen and agentic pantry with separate persistent Markdown memories for perishable ingredients and categorized pantry items, connected to leftovers, cooking history, usual meal size, per-person flavor profiles, recipe inventory, inspiration, substitutions, and variations. Use when a user wants to record groceries or pantry goods, categorize seasonings, ramen, condiments, medicine, snacks, pancake or cake mixes, or cereal, prioritize prepared leftovers, cook from ingredients on hand, reconcile food after cooking, capture meal feedback, reduce food waste, save or adapt recipes, plan meals, or initialize and maintain a Let Em Cook workspace.
---

# Let Em Cook

Operate a local-first agentic kitchen. Treat the kitchen workspace as durable memory, preserve uncertainty, and turn available ingredients into realistic cooking options.

## Act as an agentic kitchen

- Read current memory before deciding what to do.
- Take the next useful in-scope action: record food, reconcile a cooked meal, surface a leftover, organize the pantry, or rank realistic meal options.
- Ask only for missing facts that materially affect storage, safety, quantity, categorization, or the requested decision.
- Persist confirmed changes immediately, validate the workspace, and state what remains unknown.
- Keep the agentic pantry separate from the active ingredient inventory while using both food memories for recipe matching.

## Load memory first

Resolve the kitchen workspace from `LETEM_COOK_HOME` when set; otherwise use `~/.letem-cook`. Treat that directory as actual persistent memory, not a disposable output. Before answering any inventory-dependent request, read:

- `inventory.md` for the canonical current ingredient inventory
- `pantry.md` for the canonical categorized pantry memory
- `cooking-log.md` for pending post-cook checks and recent outcomes
- `people.md` for per-person flavor profiles and evidence counts
- `profile.md` for usual meal size, diners, constraints, and preferences
- `recipes.json` when saved recipes matter
- `inspiration.json` when ideas or variations matter

Do not rely on chat context as a substitute for these files. If `cooking-log.md` contains a pending inventory check, resolve it before making inventory-dependent recommendations.

Use [examples/ed-kitchen](examples/ed-kitchen) as a concrete example of a valid workspace built from a real inventory conversation. Notice that it keeps miso in the agentic pantry, preserves unknown locations and dates, records the confirmed dim sum location, and keeps the steak reconciliation pending rather than inventing facts.

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

## Maintain the agentic pantry

- Treat `pantry.md` as the only source of truth for pantry items; do not duplicate the same package in `inventory.md`.
- Put active perishables, prepared food, and leftovers in `inventory.md`. Put longer-lived pantry goods and household pantry supplies in `pantry.md`.
- Categorize every pantry row as `seasonings`, `ramen`, `condiments`, `medicine`, `snacks`, `pancake or cake mixes`, `cereal`, or `other`.
- Preserve quantity, location, best-by date, and opened state as `unknown` when the user did not supply them.
- Keep medicines for household memory only. Never treat medicine as a recipe ingredient, food, snack, substitution, or meal recommendation.
- After pantry goods are used, ask what remains when the amount materially changed, then update the quantity and opened state.
- Surface low supplies, opened packages, and known best-by dates when relevant. Do not invent restock thresholds.
- Use food pantry items together with `inventory.md` for recipe coverage and inspiration.

Use the status command to surface inventory totals, pantry category counts, and near-term use-by dates:

```bash
python3 <skill-directory>/scripts/kitchen.py status <kitchen-directory> --days 7
```

## Complete every cooking session

Treat post-cook reconciliation as mandatory, not optional.

1. When cooking begins, add the meal under `Pending inventory check` in `cooking-log.md`.
2. After the final cooking step, or as soon as the user says they finished cooking, ask: **“Are there any ingredients left? If so, what is left and about how much? How many portions of the cooked meal are left?”**
3. Ask where prepared leftovers were stored and their use-by date when those facts are unknown. Ask who ate the meal, what each person thought, and whether each would make it again when that feedback was not already supplied.
4. Wait for the answer before changing consumed quantities. Do not deduct the recipe's planned amounts automatically.
5. Update every affected row in `inventory.md` and `pantry.md`, including partial amounts, newly opened state, discarded food, and prepared leftovers. Record each prepared leftover in `inventory.md` as a meal-ready row instead of only mentioning it in the cooking log.
6. Update `Last updated`, append the result under `Cooked meals`, and remove the matching pending check.
7. Summarize attributed feedback in the cooking log, then update `people.md` and the saved recipe's `last_cooked`, rating, or notes only from supplied facts or supported patterns.
8. Run validation and briefly confirm the memory changes.

If the user does not answer the leftover question, leave the pending check in the log and do not invent an inventory update. At the start of the next kitchen interaction, ask to resolve that pending check before claiming the inventory is current.

## Maintain meal size and preferences

- Treat `profile.md` as the source of truth for household-wide meal patterns and shared defaults. Keep person-specific preferences in `people.md`.
- If usual meal size is unknown, ask once before scaling a recipe or planning portions. Store the answer as servings and note the usual number of diners when supplied.
- Scale recipe recommendations to the usual meal size by default, then account for deliberately requested leftover portions.
- Record household-wide likes, dislikes, dietary restrictions, allergies, cuisines, spice level, textures, effort, and leftover preferences only when they genuinely apply to the household.
- Keep recipe-specific feedback in the recipe or cooking log. Promote it to a general preference only when the user states it generally or a repeated pattern supports it.
- Never infer an allergy or dietary restriction from a dislike, nor erase an existing restriction without explicit confirmation.
- Do not let a household default overwrite a named person's profile.
- Update the profile timestamp whenever persistent preferences change.

## Capture people's flavor profiles

- Treat `people.md` as the source of truth for individual flavor preferences. Use a stable name or user-approved label for each person.
- Capture salt, sweetness, acidity, bitterness, umami, heat, richness, aromatics, texture, doneness, cuisines, likes, dislikes, dietary restrictions, and allergies when known.
- Attribute feedback to the person who gave it. Do not turn “everyone liked it” into individual preferences unless the participants are identified.
- Keep a one-meal reaction in `cooking-log.md`. Promote it into a person's durable profile only when they state a general preference or repeated feedback supports a pattern.
- Increment the evidence count and update `Last feedback` whenever a meal contributes to a durable profile.
- Preserve contradictions. Prefer “liked this spicy curry but usually asks for mild heat” over silently replacing either fact.
- Never let group consensus override one person's allergy or dietary restriction.

For each meal with feedback from multiple people, write this summary under the meal in `cooking-log.md`:

- **Feedback by person:** concise attributed reactions
- **Shared themes:** points of agreement, including the number of people when known
- **Differences:** disagreements or person-specific reactions
- **Next-time changes:** concrete adjustments and who they serve
- **Profile updates:** durable preferences changed, or `none` when feedback was meal-specific

Do not treat silence as approval, calculate a false consensus, or erase minority feedback. When feedback is incomplete, say who has not responded.

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
6. inventory and food-pantry coverage and missing required ingredients
7. relevant people's flavor profiles, ratings, and variety from recent meals

Offer a safe leftover as the default next meal when it can cover the requested diners. If it is short on portions, suggest a simple side or combine compatible leftovers. Respect an explicit request to cook something new, but still mention leftovers that need attention soon. Never recommend a leftover as safe when storage history is unknown or questionable.

Run deterministic pantry matching as a starting point:

```bash
python3 <skill-directory>/scripts/kitchen.py match <kitchen-directory> --top 5 --days 7
```

The match command prints ready leftovers before recipe candidates. Treat name-based recipe matches as candidates, not proof that quantities are sufficient. Check quantities and units before presenting a recipe as fully cookable.

For each recommendation, report why it fits now, what it uses, what is missing or uncertain, relevant constraints, whose flavor profile it serves, and one useful variation when it adds value. For groups, find overlap first and offer a split seasoning, sauce, garnish, or doneness strategy when preferences differ.

## Capture inspiration and variations

Use inspiration records for promising ideas that are not yet complete recipes. Base them on ingredients to use soon, complementary staples, seasonal themes, cuisines, techniques, leftovers, or user cravings. Promote an idea to `recipes.json` only after it is repeatable.

Label recipe changes as a substitution, dietary adaptation, technique variation, format variation, or scale variation. Explain important tradeoffs and prefer one to three deliberate changes over an unbounded list of swaps.

## Apply safety boundaries

- Ask about dietary restrictions or allergies when they materially affect recommendations and are not known.
- Never infer allergen-free status from an ingredient name alone.
- Do not treat a use-by date as the sole food-safety test. Call out uncertainty around storage history, spoilage, raw animal products, and leftovers.
- Distinguish food-safety guidance from taste or quality advice.
- Use authoritative local guidance for exact safe temperatures or storage windows when high-stakes food-safety advice is requested.
