---
name: glossa-fill-translations
description: Translate a Glossa project's missing strings yourself, with the whole codebase as context, instead of leaving them to AI auto-translation — list_missing_translations for the worklist (keys, file paths, glossary, rules), find where each key is used in the repository, record it with set_key_context, translate, and write back with submit_translations; also switching a project to translation_mode agent. Use for "fill the missing translations", "translate the new strings using the code", "let my agent translate instead of auto-translate", "add code context"; do not use for pushing or pulling files (glossa), working review tasks (glossa-review-queue) or audits (glossa-audit).
---

# Filling missing translations from the codebase

Glossa's AI translates a string from its text, description and the workspace
glossary. You can do better: you can open the screen, component or view where
the key is used and see whether "Open" is a button or a status, how long the
label may be, and what surrounds it. This skill is that loop. Translations you
write do not use the workspace's AI translation credits.

## Setting: who translates a project

Each project has a `translation_mode`:

- `ai` (default): Claude translates new strings into every target locale as
  soon as a source file is pushed.
- `agent`: nothing runs automatically. New strings stay missing until an agent
  (you) fills them. `push_file` returns `translation_mode: "agent"` and no
  `translate_job_id`.

Read it with `list_projects`. Switch with `update_project` and
`translation_mode: "agent"` (or in the dashboard: project settings → Who
translates). Ask the person before switching an existing project: switching
back to `ai` queues AI translation of everything still missing. The loop below
works in either mode, e.g. to translate a release's new strings yourself before
the AI would.

## Loop

1. **Orient.** `get_workspace`, `list_projects`; pick the project and confirm
   the locales with the person if they did not name them.
2. **Get the worklist.** `list_missing_translations` with `project` (and
   `locales` to narrow, `limit` up to 200). Each unit has `source_text`,
   `missing_locales`, `keys` (`key_id`, key name, project, file `path`, file
   comment, the `code_context` already recorded, and
   `previous_source_text` when the key's English changed and its old
   translation went stale: translate the new text, using the old one only to
   see what changed),
   `description`, `placeholders`, `max_length`, matching `glossary` terms and the
   `translations` it already has in other locales. The first page also returns
   `context`: the product context and prompt rules that apply (pass `project` for a
   project with its own `product_context`; its context and rules replace the
   workspace's). `total_units` is what is left.
3. **Read the code.** For each unit, search the repository for its key names
   (for example `t("settings.save")`, `R.string.save`, `NSLocalizedString`) and
   read enough of the surrounding UI to know what the string means, its tone
   and how much room it has. Group units from the same screen so you read each
   file once.
4. **Record the context.** `set_key_context` with `project` and up to 200
   `{key_id, usages: [{path, line, excerpt}], role, screen, note}`: the call
   site with a few lines of code around it, what the string is (`button`,
   `status`, `label`, `title`…), the screen, and a note when the meaning is not
   obvious ("the fare state while the taximeter is paused"). Glossa keeps it on
   the key for later agents, reviewers and Glossa's own translation and merge
   checks. Each key comes back `strong` (call site plus role, screen or
   note), `weak` or `missing`; aim for strong. Never paste secrets or
   credentials from the code into an excerpt.
5. **Translate.** Follow the glossary exactly (`do_not_translate` terms stay as
   they are), the rules and the tone of existing translations. Keep every
   placeholder from `placeholders` (`%@`, `{count}`, ICU arguments) and plural
   forms when the source has `plural`. Respect `max_length`. In an ICU message
   (`{count, plural, one {# image} other {# images}}`, `select`,
   `selectordinal`) translate only the branch text, keep argument names, select
   keys, `=0` branches, `#` and `<tags>`, and give each plural exactly the
   categories `icu_plural_categories` lists for the locale (ja: `other`; ru:
   `one few many other`). Write ’ rather than ' right before `{` or `<`.
6. **Write back.** `submit_translations` with up to 200 items
   `{unit, locale, text, note?}`. Put where and how the string is used in
   `note` when the meaning was not obvious. Use status `reviewed` (the default)
   for wordings you are sure of; send an item with `status: "needs_review"`
   when you are not, which opens a `translation_review` task for a person.
   The default `overwrite: "machine"` also replaces AI drafts but never
   reviewed, approved or imported work; do not pass `overwrite: "all"` unless
   the person asked to redo human work.
7. **Fix what was rejected.** The result lists `rejected` items (placeholder
   mismatch, unknown unit) and `skipped` ones (already translated). Correct the
   rejected ones and resubmit.
8. **Repeat** from step 2 until `total_units` is 0 (submitted units drop out of
   the list; use `offset` to skip ones you are leaving for the person).
9. **Report and pull.** Say how many strings and locales you filled, what you
   flagged for review and why, then pull the files (`pull_file`, or the
   `glossa` skill) if the person wants them in the repository.

## When the string itself is the problem

- The same text means different things in different keys (a verb on one
  screen, an adjective on another): `split_key` the odd one out with a
  description, then translate each unit on its own. The new unit uses the
  split key's own source text and placeholder names; copied translations are
  remapped to those names. Two split keys intentionally get separate units.
- A string is ambiguous for every translator: `update_unit` with a
  `description` that says what you learned from the code. It helps every
  locale and every future translator.

## From a terminal

The CLI wraps the same ops. `glossa missing --project web --locale es --out missing.json`
writes the worklist; translate it into a JSON array of
`{"unit", "locale", "text"}` and run `glossa fill translations.json` (it batches
by 200 and prints what was skipped or rejected). Any op also takes
`--json @file.json`.
