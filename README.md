# Let Em Cook

Let Em Cook is a home-chef agent skill that turns a lightweight kitchen inventory into useful meal ideas. It keeps four concerns connected:

- ingredient inventory, quantities, locations, and expiration dates
- a personal recipe inventory
- recipe inspiration based on what is available or needs to be used
- practical variations and substitutions

The first version is intentionally local-first. Kitchen data lives in readable JSON files, and the included Python CLI has no third-party dependencies.

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
```

## Start a kitchen workspace

```bash
python3 skills/letem-cook/scripts/kitchen.py init kitchen
python3 skills/letem-cook/scripts/kitchen.py validate kitchen
python3 skills/letem-cook/scripts/kitchen.py status kitchen
python3 skills/letem-cook/scripts/kitchen.py match kitchen
```

This creates:

```text
kitchen/
├── inventory.json
├── recipes.json
└── inspiration.json
```

See [the data model](skills/letem-cook/references/data-model.md) for the record formats.

## Development

```bash
python3 -m unittest discover -s tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/letem-cook
```

## License

MIT
