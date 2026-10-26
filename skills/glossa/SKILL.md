---
name: glossa
description: Translate an app's strings with Glossa — push translation files in any format (JSON, xcstrings, strings.xml, PO, XLIFF, ARB, YAML and formats Glossa learns), let Claude translate missing locales with the workspace glossary and rules, check and fix translations, and pull finished files back into the repository. Use for "translate this file", "add German", "sync translations", "what is missing in French"; do not use for translating missing strings yourself from the codebase (glossa-fill-translations), working the review queue (glossa-review-queue), locale audits (glossa-audit), unknown file formats (glossa-formats) or connection and CI setup (glossa-setup).
---

# Glossa: push, translate, pull

Glossa is translation management built for agents. Every action in its
dashboard is an **op** with the same name everywhere: an MCP tool on the
`glossa` server, `POST /api/v1/<op>` over REST, and `npx @meterapp/glossa <op> --json '{…}'`
in a terminal. This skill uses the MCP tool names; the CLI and REST take the
same JSON input.

## The model in one paragraph

A **workspace** holds **projects** (one per app or site). A project has
**files** (paths such as `locales/{locale}.json` or `ios/Localizable.xcstrings`)
and **target locales**. Every source string becomes a **key** pointing at a
**unit**: identical source text across files and projects is one unit, so it is
translated once and stays consistent everywhere. Each unit has one
**translation** per locale with a status: `machine` (Claude's draft),
`imported`, `needs_review`, `reviewed`, `approved`. Translation uses the
workspace **glossary** (`list_glossary`) and prompt **rules** (`list_rules`).
Decisions the AI is unsure about become **tasks** in a review queue.

## Workflow

1. **Orient** (free, read-only): `get_workspace`, `list_projects`. Pick the
   project the user means; if none fits, `create_project` with a slug, name and
   `target_locales` (BCP 47: `es`, `de`, `pt-BR`, `zh-Hans`). Confirm the locale
   list with the person before creating a project or adding locales: every
   added locale is translated for every unit.
2. **Push** the source file: `push_file` with `project`, `path` (as it lives in
   the repo) and `content`. Glossa detects the format (`detect_format` shows
   what it would pick). The result reports keys added/updated/removed, units
   merged into existing ones, and a `translate_job_id` when the project's
   `translation_mode` is `ai`. In `agent` mode nothing is translated
   automatically: the new strings wait for an agent, so switch to
   `glossa-fill-translations`. Status `needs_format` means no format could
   read the file: switch to `glossa-formats`.
   Pushing an already-translated locale file imports those translations as
   `imported`; it never overwrites `reviewed` or `approved` ones.
   When the push changed what a source string says (not just its case or
   placeholder names), `stale.keys` counts those keys: with the project's
   `retranslate_stale` on (the default) they are translated again
   (`stale.retranslating`); off, the old wording stays as `needs_review` with a
   `translation_review` task (`stale.kept_for_review`). A target file still
   holding the old wording is not imported onto the new text
   (`stale.skipped_imports`); pull the file to get the new translation. Before
   a release, `list_stale_translations` shows every changed key still
   `pending` in some locale.
3. **Translate**: automatic after a push in `ai` mode; to fill gaps or
   retranslate, call `translate` with the project (optionally `locales` or unit ids). Follow the
   job with `get_job` until `done`, `failed` or `cancelled` (`list_jobs` shows recent ones).
   To stop queued or running work, use `cancel_job` with `job` (CLI: `glossa cancel <job-id>`). Completed translations remain; an in-flight model request may finish.
   Large retranslations cost the workspace AI usage: say how many units and
   locales before starting one the person did not ask for. To translate the
   missing strings yourself, reading where each key is used in the code, use
   `glossa-fill-translations` (`list_missing_translations`,
   `submit_translations`); it costs no AI usage.
4. **Check**: `get_stats` for coverage per locale; `search_units` or
   `list_units` (filter by locale or status) to find strings; `get_unit` shows
   the source, every key that uses it, and all translations with history.
   Fix one with `set_translation`; mark checked ones with `review_translations`.
5. **Pull**: `pull_file` with `project`, `path` and `locale` returns the file in
   its own format, layout and comments preserved. Write it to the path the
   project uses for that locale, then show the person `git diff`.

In a terminal or CI the same loop is `npx @meterapp/glossa push <file> --project <slug>`
and `npx @meterapp/glossa pull --project <slug>` (see `glossa-setup`).

## Units: shared by default

Because units are shared, editing a translation changes it in every file and
project that uses that string. If one place needs a different translation
(the same English word, different meaning), split the key with `split_key`
rather than overwriting the shared unit. If two units are the same string with
trivial differences, `merge_units`. The review queue proposes both;
`glossa-review-queue` has the judgment rules.

## Workspaces, roles and sharing

A credential acts in one workspace with a role: `viewer` (reads only),
`member` (pushes, translates, reviews, creates projects and teams), `admin`
(also settings, billing, every API key) or `owner`. `get_account` says which
workspace and role you have; `list_members` lists the people. A project is
visible to the whole workspace (`visibility: org`) or `restricted` to its
creator, admins and the teams or people it is shared with; `list_projects`
returns your `access` (read, write, admin) on each. With admin access you can
`set_project_visibility`, `share_project` (a team or user, read/write/admin)
and `unshare_project`; `list_teams` and `create_team` manage teams. Inviting,
removing people and changing roles are done by a person in the dashboard
(Settings → Members): point them there instead of trying it.

## Glossary and rules

Before a big translation, read `list_glossary` and `list_rules`. If the person
states a preference ("never translate 'Pro'", "use informal du in German"),
add it: `upsert_glossary_term` (with `do_not_translate` for brand names) or
`add_rule` (scoped to a locale when it is locale-specific). Rules apply to
future translations; run `translate` on the affected units to apply them now.

## Answering in conversation

Report what changed in numbers (keys, units merged, locales, translations
created, tasks opened) and what is waiting on the person (review tasks,
unknown formats). Never paste an entire translated file into the chat when it
can be written to disk.

## Errors

- `401`: not connected or the key was revoked; see `glossa-setup`.
- `403 forbidden`: your role (`required_role` in the problem) or your access to the project is too low; ask a workspace admin. `403 dashboard_only`: a person does this in the dashboard.
- `404 not_found`: wrong project slug, unit id or path, or a restricted project not shared with you; list first.
- `422`: input failed validation; the problem `detail` names the field.
- A job `failed`: read its `error` with `get_job`; retry once with `translate`; report persistent failures.

## When Glossa falls short

Feedback goes straight to the team that builds Glossa, and everyone who files,
upvotes or comments gets an email at every status change.

- **A call fails in a way that looks like a Glossa bug** (a 5xx, a file that
  does not round-trip, a translation the pipeline mangled): offer to file it
  with `report_issue`, including the `request_id` from the error (every MCP tool
  error ends with one) and `context` with the `op`, `project`, `key`, `locale`
  or `file`. Issues are private to the workspace and the Glossa team. From a
  terminal, `glossa feedback report "<title>" --last` attaches the last failed
  call.
- **The person wishes Glossa did something it cannot** (a format, an op, an
  integration): `request_feature`. Feature requests are public (first names
  only), so never include keys, source strings, translations or customer names.
- Both check for duplicates. An identical item gets the vote instead; when
  `filed: false` comes back with `similar`, `upvote_feedback` the match and add
  the use case with `comment_on_feedback` rather than forcing a new item with
  `force: true`.
- `list_feedback` searches the board, `list_my_feedback` follows up on earlier
  reports, `set_feedback_subscription` turns the emails off.
- **Reviews**: when the person wants to rate Glossa, `submit_review` with their
  rating and words (ask; never write one for them). `list_reviews` reads them.
