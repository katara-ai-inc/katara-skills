# Katara Skills

Open-source agent skills for using [Katara](https://katara.ai), the hosted knowledge service for people and AI clients.

**Load knowledge once. Assign access once. Use it everywhere.** Bring authorized documents, Wiki knowledge and memory into your AI client through Katara's remote MCP service.

[Open Katara / sign up](https://app.katara.ai/) · [Connect your AI client](https://app.katara.ai/mcp) · [Documentation](https://docs.katara.ai/katara) · [Current pricing](https://katara.ai/pricing)

## Available skills

| Skill | Use it for |
| --- | --- |
| [katara](skills/katara/SKILL.md) | Connect a client, find authorized knowledge, answer with evidence, and deliberately save useful knowledge. |

These are portable [Agent Skills](https://agentskills.io/specification) instructions, not an MCP server, autonomous uploader, or Katara backend. A compatible client and Katara account with appropriate organization and resource access are required. Installing a skill does not create an account, connect MCP, grant permissions, or start a paid subscription.

## Install

Review [the skill](skills/katara/SKILL.md) and its references before installation. No installer script, background process or telemetry is bundled.

### Hermes Agent

```sh
hermes skills install katara-ai-inc/katara-skills/skills/katara
```

Optionally add this repository as a source for future skills:

```sh
hermes skills tap add katara-ai-inc/katara-skills
```

Use your client's normal MCP connection and browser authorization flow separately. Follow the current [Hermes skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/) and [Katara connection guide](https://docs.katara.ai/about/connect-ai-clients/connect).

### Other Agent Skills clients

```sh
git clone https://github.com/katara-ai-inc/katara-skills.git
```

Copy the complete `skills/katara` directory, including its references and license, into your client's documented skills directory. Do not overwrite an existing skill without reviewing its changes. Use the client's own installer/configuration instructions; the skill intentionally does not assume one client's tool names or credential storage.

## First useful result

1. **Open Katara:** sign in or sign up, and select the correct organization. Review current plan and residency choices in the application before accepting them.
2. **Prepare knowledge:** use an existing authorized source, or add a small non-sensitive document through the dashboard. Brain capabilities vary by deployment; see [onboarding](skills/katara/references/onboarding.md) for both knowledge paths.
3. **Connect:** open the MCP portal, select your organization, copy its exact connection URL, and authorize your client in the browser. Never paste bearer tokens into chat or a skill file.
4. **Ask:** “Use Katara to answer a question from this source, cite the evidence, and say if the evidence is incomplete.”
5. **Keep context deliberately:** ask to save a decision only after reviewing its destination, audience and provenance.

For example: “Connect me to Katara”; “What does our release guide say about rollbacks?”; or “Save this approved decision to the selected team Brain.” The last prompt requests a write; a lookup does not.

The skill uses only tools discovered from your live server. Documentation and implemented contracts do not guarantee a feature is enabled in your deployment. A denied read is not a reason to buy a plan or broaden access automatically.

## Design and quality

- [Skill design and SaaS activation journey](docs/skill-design.md)
- [Behavioral evaluation scenarios](evals/README.md)
- [Contributing and validation](CONTRIBUTING.md)
- [Security reporting](SECURITY.md)

Run structural checks locally with Python 3.11 or later:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

CI runs the same checks. These validate packaging and evaluation definitions, not live OAuth, permissions or model behavior. Behavioral and live SaaS acceptance remain separate gates.

## License

[Apache License 2.0](LICENSE), including its explicit contributor patent grant. The license covers this repository's skill instructions, documentation and code. Katara's hosted service, customer data, trademarks, subscription terms and third-party clients are not relicensed by this repository. No trademark rights are granted.
