# Glossa — plugin for Claude Code, Codex and Cursor

AI-native translation management by Meter, wherever your agent works. One
repository, native packaging for each client, plus the vendor-neutral
[Open Plugins](https://agent-plugins.org) manifest.

Push your app's translation files in any format — JSON, Apple `.strings` and
`.xcstrings`, Android `strings.xml`, gettext PO, XLIFF, ARB, YAML, and formats
Glossa learns from a sample — and Claude translates every missing locale with
your workspace glossary and prompt rules. Identical strings across files and
apps share one translation. A review queue collects the decisions the AI was
unsure about, locale audits answer "how is our Spanish?", and finished files
come back in their own format. [Read the docs](https://getglossa.dev/docs?ref=plugin).

## Install

### Claude Code

One step:

```text
/plugin install glossa --marketplace MeterApp/glossa-plugins
```

Or add the marketplace first, then install from it:

```text
/plugin marketplace add MeterApp/glossa-plugins
/plugin install glossa@glossa
```

### Codex

```bash
codex plugin marketplace add MeterApp/glossa-plugins
codex plugin add glossa@glossa
```

### Cursor

```bash
git clone https://github.com/MeterApp/glossa-plugins.git
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/glossa-plugins" ~/.cursor/plugins/local/glossa
```

Then reload Cursor.

### Skills only, any agent

```bash
npx skills add MeterApp/glossa-plugins
```

### Then sign in

Open `/mcp` in Claude Code, select `plugin:glossa:glossa` and authenticate in
your browser; Codex and Cursor sign in from their MCP settings. No API key or
environment variable is required. On a machine without a browser, Claude Code
offers an optional **Glossa API key** field (`/plugin` → Glossa → Configure
options): paste a key from [the dashboard](https://getglossa.dev/dashboard?ref=plugin).
It is kept in your system's secure credential store and sent only to the Glossa
MCP server.

## What it sends and fetches

The plugin is skills (Markdown instructions) plus two hosted MCP servers. It
installs no hooks or local programs; your agent reads a file and sends it only
when the task you asked for calls for it.

- **`glossa`** (`https://getglossa.dev/api/mcp`, sign-in required): when you or
  your agent call a tool, the plugin sends that tool's input to Glossa — for
  example the translation file you push, string keys and source text, glossary
  terms, rules, locales and review decisions — and fetches the result, such as
  translated files, strings, review tasks, audit findings, usage and billing
  links. Glossa stores your strings and translations in your workspace and
  translates them with Claude (Anthropic) using your glossary and rules.
- **`glossa-catalog`** (`https://getglossa.dev/api/mcp/catalog`, no sign-in):
  fetches public plans and prices and creates a Stripe Checkout link for a
  human to pay. It sends only the plan and billing interval you choose.

Requests carry an `X-Glossa-Integration: plugin` header for attribution, and,
only if you set one, your optional API key in `X-Api-Key`. Nothing is charged
without a human: paid plans start in Stripe Checkout or after you approve the
exact plan and price. See the [privacy policy](https://getglossa.dev/privacy?ref=plugin)
and [terms](https://getglossa.dev/terms?ref=plugin).

## Skills

| Skill | Use it for |
| --- | --- |
| `glossa` | Push files, translate missing locales, fix strings, pull files back |
| `glossa-fill-translations` | Translate missing strings yourself with the codebase as context, instead of AI auto-translation |
| `glossa-review-queue` | Work the review queue: merges, splits, translation reviews, rule and glossary suggestions |
| `glossa-audit` | "How is our Spanish?" — run an audit and turn findings into fixes, rules and glossary terms |
| `glossa-app-reviews` | Store App Store and Google Play reviews per language and use them as context for store listings and marketing copy |
| `glossa-formats` | Teach Glossa a file format it cannot read yet, and validate the template |
| `glossa-setup` | Connect MCP and the CLI, manage API keys, run `glossa push`/`pull` in CI |
| `glossa-billing` | Prices and plans, usage this month, and a Stripe Checkout link (or one-call upgrade) to buy a plan |

## The same ops everywhere

Every dashboard action is an op with one name across MCP tools,
`POST /api/v1/<op>` and the CLI (`npx @meterapp/glossa <op> --json '{…}'`):
workspace and projects, files and formats, units and translations, the review
queue, glossary, rules, audits, app reviews, jobs, activity, API keys and billing.

## Support

Questions and bugs: jonathan@getglossa.dev, or an issue in this repository.
