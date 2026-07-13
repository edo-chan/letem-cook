# Let Em Cook

Let Em Cook is a home-chef agent skill that turns persistent kitchen memory into useful meal ideas. It keeps five concerns connected:

- ingredient inventory, quantities, locations, and expiration dates
- prepared leftovers that should become the next meal
- a personal recipe inventory
- recipe inspiration based on what is available or needs to be used
- usual meal size, food preferences, variations, and substitutions

The system is intentionally local-first. Ingredient inventory and cooking history live in readable Markdown memory files. Recipes and inspiration use JSON where structure helps matching, and the included Python CLI has no third-party dependencies.

## Install the skill

Copy the skill into your Codex skills directory:

```bash
cp -R skills/letem-cook "${CODEX_HOME:-$HOME/.codex}/skills/letem-cook"
```

Then invoke it with prompts such as:

```text
Use $letem-cook to set up my kitchen inventory.
Use $letem-cook to tell me what I can cook tonight in 30 minutes.
Use $letem-cook to save this recipe and suggest two vegetarian variations.
Use $letem-cook to prioritize ingredients that expire this week.
Use $letem-cook to record what is left after I cooked dinner.
Use $letem-cook to remember that I usually cook for two and prefer spicy food.
```

## Start a kitchen workspace

```bash
python3 skills/letem-cook/scripts/kitchen.py init
python3 skills/letem-cook/scripts/kitchen.py validate
python3 skills/letem-cook/scripts/kitchen.py status
python3 skills/letem-cook/scripts/kitchen.py match
```

By default this creates private, persistent memory at `~/.letem-cook`. Set `LETEM_COOK_HOME` or pass a directory argument to use another location:

```text
~/.letem-cook/
├── inventory.md
├── cooking-log.md
├── profile.md
├── recipes.json
└── inspiration.json
```

`inventory.md` is the canonical ingredient and leftover memory. `profile.md` remembers normal meal size and preferences. After every cooking session, the agent asks what ingredients and portions remain, updates those files, and records the outcome in `cooking-log.md`. Safe leftovers are offered as the next meal before cooking something new. Keep this directory private; personal kitchen memory is intentionally not stored in the public repository.

See [the data model](skills/letem-cook/references/data-model.md) for the record formats.

## Example kitchen

The bundled [example kitchen](skills/letem-cook/examples/ed-kitchen) uses Ed's real starter inventory: half a T-bone steak, four croissants, two pieces of Alpaca chicken, a bento box of cooked rice, and a snack-size savory-and-sweet dim sum set. Unknown storage and dates remain unknown on purpose.

```bash
python3 skills/letem-cook/scripts/kitchen.py validate skills/letem-cook/examples/ed-kitchen
python3 skills/letem-cook/scripts/kitchen.py status skills/letem-cook/examples/ed-kitchen
```

## Development

```bash
python3 -m unittest discover -s tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/letem-cook
```

## License

MIT
