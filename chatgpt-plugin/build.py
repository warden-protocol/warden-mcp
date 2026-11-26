#!/usr/bin/env python3
"""Validate the ChatGPT plugin package and build its ZIP.

Checks follow the OpenAI plugin docs (read 26 Nov 2026):
https://developers.openai.com/plugins/build/plugins
https://developers.openai.com/plugins/deploy/submission#manifest-fields

Usage: python3 chatgpt-plugin/build.py        # validate and write dist/*.zip
       python3 chatgpt-plugin/build.py --check  # validate only
"""
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "plugin"
DIST = HERE / "dist"
ZIP_NAME = "warden-token-terminal-chatgpt-plugin.zip"

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
FORBIDDEN_KEYS = {"apps", "hooks", "test_credentials", "reviewer_instructions", "clientSecret"}
EXPECTED_TOOLS = {"list_chains", "search_tokens", "trending_tokens", "price_history", "quote_swap", "swap_status"}

errors = []


def err(msg):
    errors.append(msg)


def check_len(obj, key, limit, required=True):
    val = obj.get(key)
    if val is None:
        if required:
            err(f"missing {key}")
        return
    if not isinstance(val, str) or not val.strip():
        err(f"{key} must be a non-empty string")
    elif len(val) > limit:
        err(f"{key} is {len(val)} chars, limit {limit}")


def check_url(obj, key, limit=1024):
    val = obj.get(key)
    if not val:
        err(f"missing {key} (required for MCP review)")
    elif not val.startswith("https://") or "@" in val.split("/")[2] or len(val) > limit:
        err(f"{key} must be an HTTPS URL without credentials, at most {limit} chars")


def walk_keys(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in FORBIDDEN_KEYS:
                err(f"forbidden key {path}{k}")
            walk_keys(v, f"{path}{k}.")
    elif isinstance(node, list):
        for v in node:
            walk_keys(v, path)


def png_size(path):
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def check_icon(rel, label):
    if not rel:
        err(f"missing {label}")
        return
    if not rel.startswith("./"):
        err(f"{label} path must start with ./")
    path = SRC / rel[2:]
    if not path.is_file():
        err(f"{label} file not found: {rel}")
        return
    if path.stat().st_size > 5 * 1024 * 1024:
        err(f"{label} is over 5 MiB")
    size = png_size(path)
    if size is None:
        err(f"{label} must be a PNG")
    else:
        w, h = size
        if w != h or w < 48 or w > 4096:
            err(f"{label} must be square, 48 to 4096 px, got {w}x{h}")


def validate_schemas(plugin, mcp):
    """Validate against the published Agent Plugins schemas when jsonschema is installed."""
    try:
        import jsonschema
        import urllib.request
    except ImportError:
        print("note: jsonschema not installed, skipped schema validation")
        return
    for label, doc, url in (("plugin.json", plugin, PLUGIN_SCHEMA), ("mcp.json", mcp, MCP_SCHEMA)):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                schema = json.load(r)
        except OSError as e:
            print(f"note: could not fetch {url} ({e}), skipped schema validation")
            continue
        validator = jsonschema.validators.validator_for(schema)(schema)
        for e in validator.iter_errors(doc):
            err(f"{label} schema: {e.message}")


def main():
    plugin = json.loads((SRC / "plugin.json").read_text())
    mcp = json.loads((SRC / "mcp.json").read_text())
    walk_keys(plugin)
    walk_keys(mcp)
    validate_schemas(plugin, mcp)

    if plugin.get("$schema") != PLUGIN_SCHEMA:
        err("plugin.json $schema must be " + PLUGIN_SCHEMA)
    name = plugin.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        err("name must be lowercase letters, numbers and single hyphens, at most 64 chars")
    if not re.fullmatch(r"\d+\.\d+\.\d+", plugin.get("version", "")):
        err("version must be semver")
    check_len(plugin, "description", 4000, required=False)
    author = plugin.get("author", {})
    check_len(author, "name", 120)
    if len(plugin.get("keywords", [])) > 25:
        err("at most 25 keywords")

    oa = plugin.get("extensions", {}).get("com.openai", {})
    ui = oa.get("interface", {})
    check_len(ui, "displayName", 30)
    check_len(ui, "shortDescription", 30)
    check_len(ui, "longDescription", 4000)
    check_len(ui, "developerName", 80)
    check_len(ui, "category", 80)
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        check_url(ui, key)
    caps = ui.get("capabilities", [])
    if len(caps) > 20 or any(len(c) > 120 for c in caps):
        err("capabilities: at most 20, each at most 120 chars")
    prompts = ui.get("defaultPrompt", [])
    prompts = [prompts] if isinstance(prompts, str) else prompts
    if len(prompts) > 3 or len(set(prompts)) != len(prompts) or any(len(p) > 128 or "@" in p for p in prompts):
        err("defaultPrompt: up to 3 unique prompts, at most 128 chars, no @mentions")
    for key in ("brandColor", "brandColorDark"):
        if key in ui and not re.fullmatch(r"#[0-9A-Fa-f]{6}", ui[key]):
            err(f"{key} must be #RRGGBB")
    check_icon(ui.get("logo"), "logo")
    check_icon(ui.get("composerIcon"), "composerIcon")

    cases = oa.get("review", {}).get("test_cases", {})
    pos, neg = cases.get("positive", []), cases.get("negative", [])
    if len(pos) != 5:
        err(f"need exactly 5 positive test cases, have {len(pos)}")
    if len(neg) != 3:
        err(f"need exactly 3 negative test cases, have {len(neg)}")
    for c in pos:
        for k in ("description", "prompt", "tools_triggered", "expected_behavior"):
            if not c.get(k):
                err(f"positive case missing {k}: {c.get('description')}")
        for tool in (t.strip() for t in c.get("tools_triggered", "").split(",")):
            if tool not in EXPECTED_TOOLS:
                err(f"positive case names unknown tool {tool!r}")
    for c in neg:
        if not c.get("description") or not c.get("prompt"):
            err("negative case needs description and prompt")

    if mcp.get("$schema") != MCP_SCHEMA:
        err("mcp.json $schema must be " + MCP_SCHEMA)
    servers = mcp.get("mcpServers", {})
    if len(servers) != 1:
        err("exactly one MCP server per plugin")
    for sname, s in servers.items():
        if s.get("type") != "streamable-http" or not str(s.get("url", "")).startswith("https://"):
            err(f"server {sname}: needs type streamable-http and an HTTPS url")
        if s.get("headers"):
            err(f"server {sname}: public submission rejects nonempty headers")
        # No auth block means no authentication (the docs' remote example omits it).
        auth = s.get("extensions", {}).get("com.openai", {}).get("auth", {}).get("type", "none")
        if auth not in ("none", "oauth", "mixed"):
            err(f"server {sname}: auth type must be none, oauth or mixed for the portal")

    if errors:
        print("Validation failed:")
        for e in errors:
            print("  - " + e)
        return 1
    print(f"Valid: {name} {plugin['version']}, MCP {next(iter(servers.values()))['url']}")
    if "--check" in sys.argv:
        return 0

    DIST.mkdir(exist_ok=True)
    out = DIST / ZIP_NAME
    files = sorted(p for p in SRC.rglob("*") if p.is_file() and not p.name.startswith("."))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo(str(p.relative_to(SRC)), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    print(f"Built {out.relative_to(HERE.parent)} ({out.stat().st_size} bytes): " + ", ".join(str(p.relative_to(SRC)) for p in files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
