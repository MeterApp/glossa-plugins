# AGENTS.md — the Glossa cross-agent plugin

One plugin, packaged natively for Claude Code, Codex and Cursor, plus the
vendor-neutral Open Plugins manifest. This directory is the source of truth in
the private `MeterApp/glossa` repository and is published verbatim to the public
`MeterApp/glossa-plugins` repository, where these files sit at the root.
Everything here is customer- and agent-visible.

## The shape

| Path | Consumed by |
| --- | --- |
| `.claude-plugin/marketplace.json` | `/plugin marketplace add MeterApp/glossa-plugins` |
| `.claude-plugin/plugin.json` | `/plugin install glossa@glossa`; directory listing URLs, the optional `api_key` option and Claude Code's copy of the MCP server (replaces the `.mcp.json` entry of the same name) |
| `.agents/plugins/marketplace.json` | `codex plugin marketplace add MeterApp/glossa-plugins` |
| `.codex-plugin/plugin.json` | `codex plugin add glossa@glossa` (and the Codex listing) |
| `.cursor-plugin/plugin.json` | Cursor |
| `.plugin/plugin.json` | Open Plugins and anything that reads the portable schema |
| `.mcp.json` | Every client: the hosted server with client-managed OAuth |
| `skills/` | All of the above, and `npx skills add MeterApp/glossa-plugins` |

The marketplace `source` is `"./"`: the repository is the plugin.

## Rules

- **Manifest versions move together.** All four `plugin.json` files carry the
  same `version`, and `CHANGELOG.md` gains a `## <version> ` heading in the same
  commit. `scripts/validate_repo.py` fails otherwise.
- **Op names are exact.** Skills name ops exactly as the server registers them
  (`push_file`, `claim_tasks`, `run_audit`, …). The validator rejects a
  backticked snake_case name that is not a known op; add new ops to `OPS` in
  the validator in the same change that documents them.
- **Every production-origin link carries `?ref=`**, except the bare origin,
  `/api/*` and machine-readable files (`llms.txt`, `openapi.json`).
- **Never link the private source repository.** Link `/docs` or the public plugin repository.
- **Skill frontmatter is `name` and `description` only**, the name matches the
  folder, and the description (≥ 120 characters) says when to use the skill
  *and* when not to.
- **`agents/openai.yaml` stays in sync with its skill.** Skills that call MCP
  tools declare the `glossa` MCP dependency; `glossa-setup` does not.
- **OAuth by default, no embedded credentials.** No MCP configuration sets an
  `Authorization` header (it would disable Claude Code's OAuth sign-in). The one
  key the plugin takes is the optional, `sensitive` `api_key`, which only Claude
  Code's copy of the server sends, as `X-Api-Key`, next to
  `X-Glossa-Integration: plugin`. `.mcp.json` stays OAuth-only.
- **Nothing reads a credential from the user's machine**, not even in an
  example: no `$…_KEY` in commands, no `process.env.…KEY` in code. CI examples
  take keys from the CI's secret store. The validator enforces it.

## Safety

- Retranslating many units or adding locales spends the workspace's AI usage:
  skills tell the agent to state the size first.
- Rules and glossary terms change every future translation: skills tell the
  agent to show the wording before adding one unless the person asked.
- A wrong merge is worse than a slow one: unclear queue tasks go to the person.

## Validation

```bash
python3 scripts/validate_repo.py
claude plugin validate . --strict
CODEX_HOME="$(mktemp -d)" codex plugin marketplace add . --json
npx -y skills@latest add . --list
```
