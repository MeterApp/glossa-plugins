---
name: glossa-setup
description: Connect an agent, IDE or CI pipeline to Glossa and fix it when the tools do not appear — the hosted MCP server with browser sign-in, the optional API key in Claude Code's plugin options, manual MCP setup in Codex, Cursor and other hosts, the CLI (npx @meterapp/glossa login with browser sign-in, glossa mcp over stdio), creating and revoking API keys, and running glossa push and pull in GitHub Actions. Use for setup, keys, CI and 401 troubleshooting; do not use for translation work once connected (glossa).
---

# Connecting to Glossa

Every Glossa op is available three ways with the same names and inputs:

- **MCP** (agents and IDEs): `https://getglossa.dev/api/mcp`, Streamable HTTP, browser OAuth sign-in or an API key.
- **REST**: `POST https://getglossa.dev/api/v1/<op>` with a JSON body and an API key.
- **CLI**: `npx @meterapp/glossa <op> --json '{…}'`, plus `glossa push`, `glossa pull`, `glossa tasks` and `glossa mcp` (a local stdio MCP server).

## Plugin installs: sign in with your browser

The plugin configures the hosted server as `glossa`. No key is needed: in
Claude Code open `/mcp`, choose `plugin:glossa:glossa` and authenticate, then
approve access to your workspace in the browser. Codex and Cursor sign in
from their MCP connection settings.

**Or save an API key (Claude Code).** For a machine with no browser, the plugin
takes an optional **Glossa API key**: open `/plugin`, select Glossa, choose
**Configure options**, paste a `gls_…` key and restart. Claude Code keeps it in
the system credential store and sends it only to the Glossa server as the
`X-Api-Key` header; left empty, browser sign-in applies. The person enters the
key there themselves: never ask for a key in the conversation, and never copy
one from environment files or another tool's config.

The plugin never sets an `Authorization` header: a configured one would turn
off OAuth sign-in in Claude Code.

## CLI sign-in

```bash
npx @meterapp/glossa login
```

It prints a code like `ABCD-EFGH` and a URL (the `/activate` page, with the code filled in)
and opens the browser. The person signs in, checks the code matches and
approves; the CLI then receives a new workspace API key named
"glossa CLI on <hostname>" and saves it to `~/.config/glossa/config.json`.
An agent running the command relays the URL and code to its human and waits;
it never approves on their behalf. `--no-browser` skips opening a browser
(SSH); `login --key gls_…` saves an existing key instead. Only owners and
admins can approve, because approving creates an API key.

## API keys

Keys belong to a workspace. Owners and admins manage them with
`list_api_keys`, `create_api_key` (returns the full `gls_…` key **once**) and
`revoke_api_key`, or in the dashboard. Create one key per machine or pipeline,
named for it ("GitHub Actions — ios-app"), so it can be revoked alone. Never
paste a key into a chat, an issue, a commit or client-side code.

## Manual MCP setup

Claude Code:

```bash
claude mcp add --transport http glossa https://getglossa.dev/api/mcp
```

Then `/mcp` → authenticate. Other hosts (`.cursor/mcp.json`, Codex
`config.toml`, Claude Desktop) take the same URL as an HTTP server; hosts
without OAuth send the key as `Authorization: Bearer gls_…`.

Local stdio server (uses the key the CLI is configured with):

```bash
npx @meterapp/glossa mcp
```

## CI: keep translations in sync

Create a workspace key for CI and store it in the repository's secret store.
In the workflow, map that secret into the job's environment (an `env:` entry
on the job) under the variable name the
[CLI docs](https://getglossa.dev/docs/cli?ref=plugin#ci) give: the CLI looks
for it there. The plugin never reads it; only the CI runner does. The
[release gate recipes](https://getglossa.dev/docs/release-gate?ref=plugin#recipes)
show deploy and check workflows.

```yaml
name: Translations
on:
  push:
    branches: [main]
    paths: ["locales/en.json"]
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    # env: map your Glossa key secret here, as the CLI docs show
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: 22
      - run: npx @meterapp/glossa push locales/en.json --project my-app
      - run: npx @meterapp/glossa pull --project my-app
      - uses: peter-evans/create-pull-request@v7
        with:
          branch: glossa/translations
          title: "i18n: sync translations from Glossa"
          commit-message: "i18n: sync translations from Glossa"
```

Push on source changes; pull opens a PR with whatever is translated so far.
Machine translations arrive within minutes, so a scheduled pull (for example
nightly) picks up later review work.

To block a deploy until it is fully translated, add the release gate before
the deploy step. It counts only the strings in the commit's own source files
(so strings pushed later never block it), fails on strings never pushed, and
compares the locale files in the tree with what pull writes by SHA-256:

```yaml
      - run: npx @meterapp/glossa push
      - run: npx @meterapp/glossa pull        # skip if translations are committed
      - run: npx @meterapp/glossa check --wait 10m
```

Thresholds live in `.glossa.json` under `check` (`max_missing`, default 0;
`min_coverage`; `require_reviewed`; `stale`: fail, warn or ignore;
`allow_pending`). The op is `check_sync`; an agent can call it directly to ask
whether a branch is ready. https://getglossa.dev/docs/release-gate?ref=plugin

## Troubleshooting

- **No `glossa` tools**: the server is not connected or signed in; open `/mcp` and authenticate, then restart the host if tools still do not list.
- **401**: no credential, or the key was revoked. Sign in again (`npx @meterapp/glossa login`), or create a new key.
- **Login code expired**: codes last 15 minutes and work once; run `login` again.
- **403**: the op needs an owner or admin (API keys, workspace settings).
- **Wrong workspace**: `get_workspace` shows which workspace the credential belongs to; keys are per workspace.
