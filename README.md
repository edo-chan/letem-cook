# Let Em Cook

Let Em Cook is a home-chef agent skill that turns a lightweight kitchen inventory into useful meal ideas. It keeps four concerns connected:

- ingredient inventory, quantities, locations, and expiration dates
- a personal recipe inventory
- recipe inspiration based on what is available or needs to be used
- practical variations and substitutions

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
├── recipes.json
└── inspiration.json
```

`inventory.md` is the canonical ingredient memory. After every cooking session, the agent asks what ingredients and amounts remain, updates that file, and records the outcome in `cooking-log.md`. Keep this directory private; personal kitchen memory is intentionally not stored in the public repository.

See [the data model](skills/letem-cook/references/data-model.md) for the record formats.

## Development

```bash
python3 -m unittest discover -s tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/letem-cook
```

## License

MIT
