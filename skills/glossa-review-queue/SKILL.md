---
name: glossa-review-queue
description: Work through Glossa's review task queue quickly and with good judgment — list_tasks, claim_tasks, then resolve_tasks (batch) or resolve_task for each kind (merge_review, merge_suggestion, translation_review, glossary_suggestion, rule_suggestion, audit_finding, learn_format), including the heuristics for keeping units merged versus splitting a key. Use for "work my Glossa tasks", "clear the review queue", "should these strings be merged"; do not use for pushing or pulling files (glossa) or running audits (glossa-audit).
---

# Ripping through the Glossa review queue

Glossa's AI decides most things alone and asks only when it is unsure. Each
question is a **task**. An agent with context about the product can resolve
most of them in seconds; the queue is designed for that.

## Loop

1. `list_tasks` (filter by `kind`, `project` or `status: open`; highest
   priority first). Summarise the queue for the person: counts by kind.
2. `claim_tasks` for a batch (10–25) so no one else works the same ones.
   Claims expire; finish or release what you claim. `audit_finding` and
   `translation_review` tasks whose translation changed since they were filed
   are closed as stale on claim (`stale_closed`), so you only see live ones.
3. For each task read its `payload` (and `get_unit` for the units it names)
   and decide with the rules below. Send the batch's decisions in one
   `resolve_tasks` call (up to 50: `{ decisions: [{ task, action, note, … }] }`;
   `resolve_task` for a single one). Each `note` says what you decided and
   **why in one sentence**. A failing decision does not stop the others: check
   `results` for `ok: false` and retry or report only those. Use `dismiss` only for tasks
   that are wrong or obsolete, not to skip hard ones.
4. When unsure after reading the evidence, leave the task open and list it for
   the person with the specific question. A wrong merge or rule is worse than a
   slow one.
5. Finish with a summary: resolved by kind, left for the person and why.

## Merge or split: the core judgment

A **unit** is one source string shared by every key that uses it. Ask: *would a
good translator ever translate these occurrences differently in any of the
workspace's locales?*

Keep merged / merge when:
- The source text and meaning are the same (same UI role: both buttons, both titles), even if keys differ (`common.save`, `settings.save_button`).
- Differences are only whitespace, trailing punctuation or capitalisation that the UI applies anyway — and the person's style allows it.
- The strings are long sentences with identical wording: context rarely changes their translation.

Split (`split_key`) / do not merge when:
- The same word plays a different part of speech or meaning: "Open" (verb, button) vs "Open" (adjective, status); "Post", "Order", "Share", "Back", "Free".
- Gender, number or case agreement differs by context: "New" for a feminine vs masculine noun in Spanish or French; "All" with different nouns in German.
- Length constraints differ (a tab label with `max_length` vs a sentence).
- One occurrence has placeholders, plural forms or markup the other lacks.
- The key's file comment or description says the context differs.

`merge_review` asks whether keys **already auto-merged** should stay together;
`merge_suggestion` proposes merging **near-duplicate** units. For
`merge_suggestion`, choose the better source wording as the survivor and check
that the translations you keep are the reviewed ones.

## Other kinds

- `translation_review`: compare source, translation, glossary and rules. Fix
  with `set_translation` and resolve, or mark it fine with `review_translations`
  and resolve. Check placeholders (`{name}`, `%@`, `%1$s`, ICU plurals), length
  and tone exactly.
- `glossary_suggestion`: accept with `upsert_glossary_term` when the term is a
  product name, brand or domain term that must be consistent; reject generic words.
- `rule_suggestion`: accept with `add_rule` only when the rule is general,
  correct for the locale and backed by the examples in the payload; edit the
  wording first if needed. Rules change every future translation: when in doubt,
  leave it for the person.
- `audit_finding`: apply the proposed fix (`set_translation`, a rule or a
  glossary term) when the evidence is right; see `glossa-audit`.
- `learn_format`: see `glossa-formats` (`approve_format` after checking the template).

## Etiquette

- Resolve with reasons; they are the audit trail (`list_activity`).
- Never bulk-approve translations you have not read.
- Ask before accepting a rule or glossary term that changes the person's brand voice.
