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
| `.claude-plugin/plugin.json` | `/plugin install glossa@glossa`; Claude Code's copy of the MCP servers, identical to `.mcp.json`; listing URLs live in `.codex-plugin` and the directory listing |
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
  commit. The validator fails otherwise.
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
- **OAuth only; the plugin does no authentication.** Every MCP entry is a URL
  plus `X-Glossa-Integration: plugin`; the host signs the person in with their
  browser from the server's 401 challenge. No `userConfig`, no `Authorization`
  or key header, and the Claude manifest's `mcpServers` equal `.mcp.json`.
- **No file shows a key being read**, not even in an example or a sentence
  that denies it. Keys are created in the dashboard and kept as CI secrets;
  skills link the docs for how code and CI load them. The validator enforces it.
- **No scripts ship.** The structure validator lives in the private source
  repository (it has to name credential patterns to reject them, and the
  Claude directory's scan reads a shipped script that names them as
  forwarding the installer's key).

## Safety

- Retranslating many units or adding locales spends the workspace's AI usage:
  skills tell the agent to state the size first.
- Rules and glossary terms change every future translation: skills tell the
  agent to show the wording before adding one unless the person asked.
- A wrong merge is worse than a slow one: unclear queue tasks go to the person.

## Validation

Structure, manifests, op names and links are checked in the source
repository on every PR, before anything is published here. In this
directory:

```bash
claude plugin validate . --strict
claude plugin validate . --strict --profile directory
CODEX_HOME="$(mktemp -d)" codex plugin marketplace add . --json
npx -y skills@latest add . --list
```
