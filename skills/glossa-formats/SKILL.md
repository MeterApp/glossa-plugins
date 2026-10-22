---
name: glossa-formats
description: Handle translation files Glossa cannot read yet — detect_format to see what Glossa would pick, learn_format to have AI write a reusable template from a sample, check the template's round trip on real keys, plurals, placeholders and comments, then approve_format and push again. Use when a push returns needs_format, for unusual or in-house formats, or "does Glossa support X"; do not use for supported formats (glossa).
---

# Unknown formats

Glossa reads common translation formats with built-in parsers (`list_formats`
shows them: JSON and i18next, YAML, Apple .xcstrings, .strings and
.stringsdict, Android strings.xml, gettext PO, XLIFF, ARB, Java .properties,
RESX and CSV). Anything else is **learned**: Claude reads a
sample and writes a declarative template, which becomes a reusable format for
the workspace. The upload that could not be read waits on a `learn_format`
task until a template is approved.

## Workflow

1. `detect_format` with the file `path` and `content` (or a representative
   excerpt): it returns the best match and its confidence. A confident match is
   a supported format; use `glossa`.
2. If nothing matches (or `push_file` returned `needs_format`), call
   `learn_format` with the sample. Give the most complete sample you have:
   plurals, comments, placeholders, nested keys and escaping all need to appear
   in it to be learned. Follow the job with `get_job`.
3. **Validate the template before approving it.** The learned format is a
   draft. Check that:
   - every key in the sample was found, with the right key names (nested keys dot-joined);
   - values keep placeholders (`{name}`, `%@`, `%1$s`, `{{x}}`) and escaping exactly;
   - plural forms are read as plurals, not as separate keys;
   - comments or descriptions are attached to the right keys;
   - writing it back (`pull_file` after the import) reproduces the file's layout closely enough for a clean diff.
   If something is wrong, run `learn_format` again with a note describing the
   problem, or a better sample.
4. `approve_format` makes the template active for the workspace. Then push the
   waiting file again (`push_file`), or resolve its `learn_format` task with
   `resolve_task`.

## Good to know

- Approved templates are reused for every later file that matches, in every
  project of the workspace.
- A format that many teams need becomes a built-in parser in a later release;
  existing templates keep working.
- Never approve a template that drops placeholders or plurals: translations
  pulled through it would break the app at runtime.
- Files often spell one language differently: iOS `zh-Hans`, Android `iw` or
  `in-rID`, a web app `ar-SA`. When `push_file` warns that a locale is not a
  target locale, map it with `update_project` `locale_aliases`
  (`{"zh-Hans": "zh-CN", "iw": "he"}`, Crowdin's `languages_mapping`) and push
  again. Each file remembers its own spelling (`list_files` → `locale_codes`),
  so `pull_file` writes `values-iw/` and `"zh-Hans"` back unchanged.
