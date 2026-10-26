#!/usr/bin/env python3
"""Validate the cross-agent Glossa plugin without modifying anything.

Runs against this directory in the source repository and, unchanged, against
the published `MeterApp/glossa-plugins` repository, where these files sit at
the root. Anything that would break an install — manifests out of sync, a skill
missing its Codex interface, a relative path pointing at nothing, an op name
the server does not have, a credential read from the user's machine — fails
here rather than for a user.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

PLUGIN_NAME = "glossa"
MARKETPLACE_NAME = "glossa"
ORIGIN = "https://getglossa.dev"
MCP_URL = f"{ORIGIN}/api/mcp"
INTEGRATION_HEADER = {"X-Glossa-Integration": "plugin"}
# The source repository is private; a link there 404s outside the org.
# Assembled from parts so this file is not itself a violation.
PRIVATE_REPO = "/".join(("github.com", "MeterApp", "glossa")) + "/"
PUBLIC_REPO = "https://github.com/MeterApp/glossa-plugins"

SKILLS = ["glossa", "glossa-fill-translations", "glossa-review-queue", "glossa-audit", "glossa-formats", "glossa-setup", "glossa-billing", "glossa-app-reviews"]
# Skills that tell the agent to call MCP tools declare the dependency so Codex
# can offer to connect the server when the skill is invoked.
MCP_DEPENDENT = {"glossa", "glossa-fill-translations", "glossa-review-queue", "glossa-audit", "glossa-formats", "glossa-billing", "glossa-app-reviews"}

# Every op the server exposes (lib/ops/registry.ts). Same names over MCP, REST
# (POST /api/v1/<op>) and the CLI.
OPS = {
    "get_workspace", "update_workspace", "get_stats",
    "list_projects", "create_project", "update_project",
    "list_files", "push_file", "pull_file",
    "detect_format", "list_formats", "learn_format", "approve_format",
    "search_units", "list_units", "get_unit", "update_unit", "set_translation", "review_translations", "translate",
    "list_missing_translations", "list_stale_translations", "list_translations_for_audit", "submit_translations",
    "set_key_context", "list_weak_context",
    "merge_units", "split_key",
    "list_tasks", "claim_tasks", "resolve_task", "resolve_tasks", "recheck_merge_reviews",
    "list_glossary", "upsert_glossary_term", "delete_glossary_term",
    "list_rules", "add_rule", "update_rule",
    "list_feedback", "get_feedback", "request_feature", "report_issue",
    "upvote_feedback", "remove_feedback_vote", "comment_on_feedback",
    "list_my_feedback", "set_feedback_subscription", "submit_review", "list_reviews",
    "update_feedback", "respond_to_feedback", "respond_to_review",
    "run_audit", "get_audit", "list_audits",
    "import_app_reviews", "list_app_reviews", "get_app_review_stats", "delete_app_reviews",
    "get_job", "list_jobs", "cancel_job", "list_activity",
    "list_api_keys", "create_api_key", "revoke_api_key",
    "list_members", "list_invites", "list_teams", "create_team", "update_team", "delete_team", "set_team_member", "remove_team_member",
    "list_project_access", "set_project_visibility", "share_project", "unshare_project", "list_audit_log",
    "get_pricing", "get_account", "get_billing", "create_checkout_link", "claim_checkout", "subscribe", "cancel_subscription", "resume_subscription", "create_billing_portal_link", "get_billing_link",
}
# Task kinds share verb prefixes with ops; they are not ops.
TASK_KINDS = {"merge_review", "merge_suggestion", "learn_format", "translation_review", "audit_finding", "rule_suggestion", "glossary_suggestion"}
OP_PREFIX = re.compile(
    r"`((?:get|list|import|create|update|push|pull|detect|learn|approve|search|set|review|merge|split|claim|resolve|upsert|delete|add|run|revoke|report|upvote|remove|comment|submit|share|unshare)_[a-z_]+)`"
)


def error(message: str) -> None:
    ERRORS.append(message)


def load_json(relative: str) -> dict:
    try:
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{relative}: invalid or unreadable JSON: {exc}")
        return {}


def check_path(owner: str, value: object) -> None:
    """A manifest path must be relative, stay inside the plugin, and exist."""
    if not isinstance(value, str) or not value.startswith("./"):
        error(f"{owner}: expected a ./-prefixed relative path, got {value!r}")
        return
    target = (ROOT / value[2:]).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        error(f"{owner}: path escapes the plugin root")
        return
    if not target.exists():
        error(f"{owner}: referenced path does not exist: {value}")


# --- manifests -------------------------------------------------------------

MANIFESTS = {
    "open": ".plugin/plugin.json",
    "claude": ".claude-plugin/plugin.json",
    "codex": ".codex-plugin/plugin.json",
    "cursor": ".cursor-plugin/plugin.json",
}
manifests = {surface: load_json(path) for surface, path in MANIFESTS.items()}

versions = {surface: manifest.get("version") for surface, manifest in manifests.items()}
if len(set(versions.values())) != 1 or None in versions.values():
    error(f"manifest versions are not synchronized: {versions}")
else:
    version = next(iter(versions.values()))
    if f"## {version} " not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        error(f"CHANGELOG.md has no entry for {version}")

for surface, manifest in manifests.items():
    if manifest.get("name") != PLUGIN_NAME:
        error(f"{surface} manifest name must be {PLUGIN_NAME}")
    if manifest.get("repository") not in (None, PUBLIC_REPO):
        error(f"{surface} manifest repository must be {PUBLIC_REPO}")
    for field in ("skills", "mcpServers", "logo"):
        if isinstance(manifest.get(field), str):
            check_path(f"{surface}.{field}", manifest[field])
    interface = manifest.get("interface", {})
    if isinstance(interface, dict):
        for field in ("composerIcon", "logo", "logoDark"):
            if field in interface:
                check_path(f"{surface}.interface.{field}", interface[field])

# --- file sizes ------------------------------------------------------------

for path in ROOT.rglob("*"):
    if path.is_file() and ".git" not in path.parts and path.stat().st_size >= 256 * 1024:
        error(f"{path.relative_to(ROOT)}: {path.stat().st_size} bytes; keep every file under 256 KiB")

# --- marketplaces ----------------------------------------------------------

claude_marketplace = load_json(".claude-plugin/marketplace.json")
if claude_marketplace.get("name") != MARKETPLACE_NAME:
    error(f".claude-plugin/marketplace.json name must be {MARKETPLACE_NAME}")
claude_plugins = claude_marketplace.get("plugins", [])
if len(claude_plugins) != 1 or claude_plugins[0].get("name") != PLUGIN_NAME:
    error(f".claude-plugin/marketplace.json must list exactly one plugin named {PLUGIN_NAME}")
elif claude_plugins[0].get("source") != "./":
    error('.claude-plugin/marketplace.json source must be "./" (the repository is the plugin)')

agents_marketplace = load_json(".agents/plugins/marketplace.json")
if agents_marketplace.get("name") != MARKETPLACE_NAME:
    error(f".agents/plugins/marketplace.json name must be {MARKETPLACE_NAME}")
agents_plugins = agents_marketplace.get("plugins", [])
if len(agents_plugins) != 1 or agents_plugins[0].get("name") != PLUGIN_NAME:
    error(f".agents/plugins/marketplace.json must list exactly one plugin named {PLUGIN_NAME}")

# --- directory listing -----------------------------------------------------

codex_interface = manifests["codex"].get("interface", {})
LISTING_URLS = {
    "privacyPolicyUrl": ("privacyPolicyURL", f"{ORIGIN}/privacy?ref=plugin"),
    "termsOfServiceUrl": ("termsOfServiceURL", f"{ORIGIN}/terms?ref=plugin"),
    "supportUrl": ("supportURL", None),
}
for field, (codex_field, required) in LISTING_URLS.items():
    value = manifests["claude"].get(field)
    if not value or (required and value != required):
        error(f"claude manifest {field} must be {required or 'set'}, got {value!r}")
    elif value != codex_interface.get(codex_field):
        error(f"claude manifest {field} must match the codex interface {codex_field}")

# --- MCP server ------------------------------------------------------------

# Any configured Authorization header disables Claude Code's OAuth fallback,
# whatever its value. .mcp.json (read by Codex and Cursor too) is OAuth-only.
mcp_servers = load_json(".mcp.json").get("mcpServers", {})
# The catalog server (prices, checkout before signup) needs no credential at all.
CATALOG = {f"{PLUGIN_NAME}-catalog": {"type": "http", "url": MCP_URL + "/catalog", "headers": INTEGRATION_HEADER}}
expected = {"type": "http", "url": MCP_URL, "headers": INTEGRATION_HEADER}
if mcp_servers != {PLUGIN_NAME: expected, **CATALOG}:
    error(f".mcp.json must configure exactly {{{PLUGIN_NAME!r}: {expected}, **{CATALOG}}}, got {mcp_servers}")

# Claude Code's copy adds the optional key as X-Api-Key, never Authorization:
# an empty option is an empty header and OAuth still applies.
claude_expected = {PLUGIN_NAME: {"type": "http", "url": MCP_URL, "headers": {**INTEGRATION_HEADER, "X-Api-Key": "${user_config.api_key}"}}, **CATALOG}
if manifests["claude"].get("mcpServers") != claude_expected:
    error(f"claude manifest mcpServers must be exactly {claude_expected}, got {manifests['claude'].get('mcpServers')}")

user_config = manifests["claude"].get("userConfig")
option = user_config.get("api_key") if isinstance(user_config, dict) else None
if not isinstance(option, dict) or set(user_config) != {"api_key"}:
    error("claude manifest userConfig must declare exactly one option, api_key")
else:
    if option.get("type") != "string" or option.get("sensitive") is not True:
        error("userConfig.api_key must be a string with sensitive: true")
    if option.get("required") is True:
        error("userConfig.api_key must stay optional: browser sign-in is the default")
    if option.get("default") != "":
        error('userConfig.api_key default must be "" so an unset key is an empty header')

for path in ROOT.rglob("*.json"):
    if ".git" in path.parts:
        continue
    if re.search(r'"authorization"\s*:', path.read_text(encoding="utf-8"), re.IGNORECASE):
        error(f"{path.relative_to(ROOT)}: configures an Authorization header (disables OAuth sign-in)")

# --- skills ----------------------------------------------------------------

found = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
if found != sorted(SKILLS):
    error(f"skills/ must contain exactly {sorted(SKILLS)}, got {found}")

for name in found:
    skill_file = ROOT / "skills" / name / "SKILL.md"
    openai_file = ROOT / "skills" / name / "agents" / "openai.yaml"
    if not skill_file.exists():
        error(f"{name}: missing SKILL.md")
        continue
    if not openai_file.exists():
        error(f"{name}: missing agents/openai.yaml")
        continue
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        error(f"{name}: SKILL.md has no frontmatter")
        continue
    metadata = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("\"'")
    if set(metadata) != {"name", "description"}:
        error(f"{name}: frontmatter must contain only name and description")
    if metadata.get("name") != name:
        error(f"{name}: frontmatter name does not match the folder")
    if len(metadata.get("description", "")) < 120:
        error(f"{name}: description is too short for reliable discovery")

    openai = openai_file.read_text(encoding="utf-8")
    if f"${name}" not in openai:
        error(f"{name}: default_prompt must mention ${name}")
    if name in MCP_DEPENDENT:
        if MCP_URL not in openai:
            error(f"{name}: must declare the hosted MCP dependency")
    elif "dependencies:" in openai:
        error(f"{name}: declares an MCP dependency it does not need")

# --- op names --------------------------------------------------------------

for markdown in sorted(ROOT.rglob("*.md")):
    if ".git" in markdown.parts:
        continue
    text = markdown.read_text(encoding="utf-8")
    for match in OP_PREFIX.finditer(text):
        token = match.group(1)
        if token not in OPS and token not in TASK_KINDS:
            line = text.count("\n", 0, match.start()) + 1
            error(f"{markdown.relative_to(ROOT)}:{line}: `{token}` is not a Glossa op")

# --- local links -----------------------------------------------------------

link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for markdown in ROOT.rglob("*.md"):
    if ".git" in markdown.parts:
        continue
    for target in link.findall(markdown.read_text(encoding="utf-8")):
        target = target.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        if not (markdown.parent / target).resolve().exists():
            error(f"{markdown.relative_to(ROOT)}: broken local link {target}")

# --- things that must never ship -------------------------------------------

FORBIDDEN = {
    PRIVATE_REPO: "a link to the private source repository",
    "gls_live": "something shaped like a real API key",
    "[TODO": "an unresolved placeholder",
}
CREDENTIAL_READS = re.compile(
    r"\$\{?[A-Z][A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)\b"  # $GLOSSA_API_KEY, ${TOKEN}
    r"|\$\{\{\s*secrets\.[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)\b"  # a CI secret interpolated in an example
    r"|process\.env(?:\.|\[\s*['\"])[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)\b"
    r"|\bos\.(?:environ|getenv)\b"
    r"|Deno\.env\.get\("
    r"|import\.meta\.env\.[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)\b"
)
# Every published production link needs ?ref= for attribution, except the bare
# origin, the API and machine-readable files.
REF_EXEMPT = re.compile(rf"{re.escape(ORIGIN)}(?:/(?:api/|openapi\.json|llms(?:-full)?\.txt)|[\s\"'`)\],]|$)")

for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.parts or path.suffix in {".svg", ".pyc"}:
        continue
    if path.resolve() == Path(__file__).resolve():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    relative = path.relative_to(ROOT)
    for needle, label in FORBIDDEN.items():
        if needle in text:
            error(f"{relative}: contains {label}: {needle}")
    for match in CREDENTIAL_READS.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        error(f"{relative}:{line}: reads a credential from the user's machine: {match.group(0)}")
    for match in re.finditer(re.escape(ORIGIN) + r"[^\s\"'`)\],]*", text):
        url = match.group(0)
        if "?ref=" in url or REF_EXEMPT.match(url):
            continue
        error(f"{relative}: production link without ?ref=: {url}")

if ERRORS:
    print("Plugin validation failed:", file=sys.stderr)
    for item in ERRORS:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

print(f"Plugin validation passed: {len(manifests)} manifests, {len(found)} skills, {len(OPS)} ops")
