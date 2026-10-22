---
name: glossa-audit
description: Ask Glossa how a locale is doing ("how is our Spanish?") and fix it — with a codebase in view, audit inline (list_translations_for_audit, read the call sites of ambiguous strings, fix with submit_translations or set_translation, and propose rules and glossary terms to the person before adding them), filing no queue tasks; with no codebase, run_audit and get_audit. Use for locale quality questions and audit follow-up; do not use for translating missing strings (glossa-fill-translations) or general queue work (glossa-review-queue).
---

# Locale audits

There are two ways to audit a locale. Pick by what you can see.

- **Inline (you have the codebase).** You read the translations yourself,
  open the code that uses the ambiguous ones, and fix what is wrong straight
  away. Nothing goes to the review queue. Use this whenever the repository
  that uses the strings is open in front of you.
- **`run_audit` (no codebase).** Claude reads a sample of strings with no
  access to the code and files `audit_finding`, `rule_suggestion` and
  `glossary_suggestion` tasks for a person to decide. Use it only from a chat
  with no repository, or when the person asks for it by name.

`run_audit` cannot tell whether "Open" is a button or a status, or what a
fragment like "and {count} more" is joined to. It files a task for each
guess, so on a large workspace the queue fills faster than anyone works it.
Inline you can check the code and settle each string yourself.

## Inline audit

1. **Orient.** `get_workspace`, `get_stats` for the locale's size and status
   mix, `list_projects` to match the repository to a project. Agree the locale
   and the question with the person ("Is the tone consistently informal?",
   "Are button labels too long?"); without one, the question is "what is
   wrong, worst first".
2. **Read the sample.** `list_translations_for_audit` with `locale`,
   `project` (the repository's project) and `limit` up to 200. To audit AI
   output only, pass `status: ["machine", "needs_review"]`. Each item has
   `source_text`, the translation `text`, `status`, `origin`, `keys` (key name,
   project, file `path`, file comment), `description`, `placeholders`,
   `max_length`, matching `glossary` terms and `flags`. The first page also
   returns `context`: product context, the locale's glossary and the rules
   that apply. Page with `offset`. On a large locale, `flagged_only: true`
   returns only the flagged items.
3. **Check every item, and read the code where the flag asks for it.** The flags say where:
   - `placeholder_mismatch`, `glossary_miss`, `same_as_source`: usually wrong
     on their face; confirm and fix.
   - `short_label`: a button, a menu item, a status or a noun? Search the
     repository for the key (`t("toolbar.open")`, `R.string.open`,
     `NSLocalizedString("open"`) and read the component.
   - `fragment`: find the code that joins it with other strings. The word
     order may need the whole sentence in one string; tell the person when the
     code should change, and do not patch around it.
   - `no_context`: read the call site; if the meaning was not obvious, add a
     description with `update_unit` so every locale and every future
     translation gets it.
   Read every unflagged item too, against the glossary, the rules and the
   question asked. Group items by file so you open each screen once.
4. **Fix what is wrong.** Decide each one yourself:
   - AI drafts (`machine`, `needs_review`): rewrite with
     `submit_translations` (up to 200 items `{unit, locale, text, note}`; put
     where the string is used in `note`). The default `overwrite: "machine"`
     replaces drafts and never touches reviewed, approved or imported work.
   - Reviewed, approved, imported or human work: a person chose that wording.
     Show the person the current and proposed text and why; change it with
     `set_translation` only after they agree.
   - Not sure? Leave it as it is and list it in your report. Do not send
     `status: "needs_review"`: that files a `translation_review` task, and an
     inline audit files no tasks.
   Remember units are shared: a fix changes every key that uses the unit. If
   one call site needs a different wording, `split_key` first (see `glossa`).
5. **Prevent the pattern.** When several fixes share one cause, propose a
   rule (`add_rule`, scoped to the locale, short and general: "Use 'du',
   never 'Sie'") or a glossary term (`upsert_glossary_term` for brand names,
   product names and terms with one required translation). Check
   `list_rules` and `list_glossary` (or `context`) first and prefer
   `update_rule` over a near-duplicate. A rule that fits one string is a
   translation fix, not a rule. Rules and terms change every future
   translation in the workspace, so **show the person the exact wording and
   add it only after they approve it.**
6. **Apply rules to what is already there.** A new rule or term does not
   rewrite existing translations. Fix the affected drafts in the same pass
   with `submit_translations`, or, if the person prefers AI, `translate` with
   those unit ids (this uses AI credits; give the count first).
7. **Report.** The question's answer in a few sentences, the top problems,
   how many you fixed (with a few before → after examples), descriptions
   added, rules and terms added with their wording, code changes you
   recommend (fragments, labels that do not fit) and what you left for the
   person.

## `run_audit` (no codebase)

1. `list_audits` to see whether a recent audit already answers the question.
2. `run_audit` with `locale` and a `question`. An audit uses AI on the
   workspace's account: run one per question, not one per idea.
3. Follow the returned job with `get_job` until `done`; then `get_audit` for
   the score, summary and findings.
4. Resolve its tasks with judgment (`glossa-review-queue`): apply an
   `audit_finding` only when the fix is right for that string; accept a
   `rule_suggestion` or `glossary_suggestion` only when it fits several
   findings and does not repeat an existing rule or term; dismiss the rest with
   the reason. Show the person rule and term wording before accepting, unless
   they asked you to apply the audit's suggestions.

A follow-up audit with the same question a few days later shows whether the
fixes and rules worked.
