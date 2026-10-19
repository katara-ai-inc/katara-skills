# Contributing

Contributions are accepted under Apache-2.0. Keep skills portable and grounded in the current public service contracts.

## Add or change a skill

1. Use `skills/<skill-name>/SKILL.md` with valid Agent Skills frontmatter.
2. Keep the description specific enough for intent-based discovery. Put detailed procedures under `references/` using relative Markdown links.
3. Include `LICENSE` and `NOTICE` in the skill directory when distributing it independently.
4. Prefer live MCP discovery over hardcoded tool payloads, mutable plans or undocumented endpoints. Never add real user data or credentials.
5. Cover material behavior changes with evaluation scenarios; distinguish expected behavior from actually executed model/service results.
6. Update the README inventory when adding a skill.

## Verify

Use Python 3.11 or later and install `requirements-dev.txt` in a virtual environment. Run:

```sh
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

Validation is offline; do not log in, upload files, change permissions, buy plans or run behavioral writes as a side effect of these commands. For live smoke tests, get explicit target/action authorization and report exact evidence without customer payloads or secrets.

In a pull request, describe the user outcome, contract sources, verification performed, any unavailable live checks, and whether the main skill's activation scope changed.
