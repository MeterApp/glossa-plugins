# Changelog

## 0.13.1 — 2026-10-26

- The listing icon is found where the Claude directory looks for it by default, so no manifest names it any more.
- Author and marketplace owner read "Glossa by Meter". The plugin's install id stays `glossa`.
- `glossa-setup`: the CI section says in prose how the workflow gets its Glossa key from the CI's secret store and links the docs for the full mapping; no example interpolates a key.
- Skill wording: values are set, sent or included, a phrasing the Claude directory's scan no longer reads as a credential.

## 0.13.0 — 2026-10-23

- Exception-based merge review: the workspace's **merge_policy** (**exceptions** by default, **review_all**, **context_required**) decides when keys sharing a string need a person. Safe merges are accepted without a task; a `merge_review` names its `conflicting_key_ids`, and `split` without `key_ids` splits only those. `recheck_merge_reviews` re-applies the policy to the open queue. The `glossa-review-queue` skill settles reviews with code context.

## 0.12.0 — 2026-10-22

- Claude's translations read the keys' code context, and every AI translation stores the model's `confidence`, `context_quality` and, when context was weak, `context_needed` (the question that would settle it). `list_weak_context` lists those strings with their keys; `set_key_context` takes `retranslate: true` to redo the drafts with the new context. `glossa-fill-translations` works the weak-context list.

## 0.11.0 — 2026-10-22

- The marketplace is now named `glossa`, so it can be added next to other Meter marketplaces: install with `/plugin install glossa@glossa` (Codex: `codex plugin add glossa@glossa`), or in one step with `/plugin install glossa --marketplace MeterApp/glossa-plugins`.
- A square PNG listing icon for the plugin directory, and the README says what the plugin sends to and fetches from Glossa.

## 0.10.0 — 2026-10-21

- Source-code context: `set_key_context` records where keys are used (usages with path, line and code excerpt, UI role, screen, note) and rates each key strong, weak or missing. `glossa-fill-translations` records it for every key it translates; `list_missing_translations` and `get_unit` return `key_id` and the recorded `code_context`.

## 0.9.0 — 2026-10-21

- New `glossa-app-reviews` skill: store an app's App Store and Google Play reviews per language with `import_app_reviews` (idempotent by store review id), see which languages have them with `get_app_review_stats`, and read them with `list_app_reviews` (filter by locale, store, rating, text or date) before writing or translating store listings and marketing copy. `delete_app_reviews` removes them. `list_missing_translations` reports a project's review counts per locale in its first-page `context.app_reviews`.

## 0.8.0 — 2026-10-19

- `glossa-audit` audits inline when the codebase is in view: `list_translations_for_audit` returns a locale's existing translations with their keys, file paths, glossary, rules and flags (placeholder_mismatch, glossary_miss, same_as_source, short_label, fragment, no_context); the agent reads the call sites, fixes drafts with `submit_translations`, and adds rules and glossary terms only after the person approves the wording. It files no review tasks. `run_audit` remains for chats with no codebase.

## 0.7.0 — 2026-10-19

- Stale translations: when a push changes what a source string says, the key's old translations are stale. `push_file` reports them under `stale` (keys changed, translations being redone or kept for review, target-file entries refused because they still hold the old wording). The new `retranslate_stale` project setting (default on) translates them again; off keeps the old wording as `needs_review` with a `translation_review` task. `list_stale_translations` lists changed keys and each locale's state, and `list_missing_translations` shows a changed key's `previous_source_text`.

## 0.6.0 — 2026-10-19

- Cancel queued or running jobs with `cancel_job` or `glossa cancel <job-id>`. Completed work remains in place; the main skill includes the new terminal `cancelled` status.

## 0.5.0 — 2026-10-18

- Workspaces are shared: roles (viewer, member, admin, owner), teams and per-project sharing. The `glossa` skill explains `get_account`'s role, `list_members`, `list_teams`, `create_team`, `list_project_access`, `set_project_visibility`, `share_project` and `unshare_project`, and the new `403` cases (`required_role`, `dashboard_only`).

## 0.4.0 — 2026-10-17

- New `glossa-catalog` MCP server (no sign-in): `get_pricing` and `create_checkout_link`, so an agent can quote prices and hand a human a checkout link before anyone has an account.
- `glossa-billing` uses the pricing document every Meter product shares (`price {monthly, yearly}`, `included`, `limits`, `checkout_url`), `get_account` (usage against every limit and what the next plan adds), `get_billing_link`, and `claim_checkout` for a plan paid before signup.

## 0.3.0 — 2026-10-16

- New `glossa-fill-translations` skill: translate missing strings yourself with the codebase as context — `list_missing_translations` returns each missing string with its keys, file paths, glossary terms and rules; `submit_translations` writes up to 200 at once without using AI translation credits.
- Projects have a `translation_mode`: `ai` (Claude translates on push, the default) or `agent` (nothing runs automatically; an agent fills the missing strings). The `glossa` skill explains both.

## 0.2.0 — 2026-10-16

- New `glossa-billing` skill: read prices with `get_pricing`, check the plan and usage with `get_billing`, and buy or change a plan with `create_checkout_link` (a Stripe Checkout link for the human) or `subscribe` (the saved card, once the human approved the price). Invoices and cancellation through `create_billing_portal_link` and `cancel_subscription`.

## 0.1.0 — 2026-10-16

- First release: the hosted Glossa MCP server (browser sign-in, optional API key in Claude Code sent as `X-Api-Key`) and five skills: `glossa`, `glossa-review-queue`, `glossa-audit`, `glossa-formats` and `glossa-setup`.
