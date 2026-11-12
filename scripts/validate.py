#!/usr/bin/env python3
"""Validate local package structure and optionally check submission blockers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import urllib.request

from jsonschema import Draft202012Validator, FormatChecker, ValidationError, validators
from PIL import Image, ImageChops
import regex

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_URL = "https://developer.microsoft.com/json-schemas/teams/v1.30/MicrosoftTeams.schema.json"
EXPECTED = set("get_guide get_fax_capabilities prepare_fax get_fax_document quote_fax send_approved_fax get_fax_status list_faxes get_fax_balance cancel_fax request_card_payment get_card_payment_status request_human_review get_review_status list_inbox read_inbound_fax extract_fax_data".split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON member in {path.name}")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-schema", action="store_true", help="Verify the pinned schema against a fresh Microsoft download")
    parser.add_argument("--check-hosted", action="store_true", help="Compare tools/list with the packaged definitions without executing tools")
    parser.add_argument("--submission", action="store_true", help="Also reject an unset credential reference and check hosted parity")
    args = parser.parse_args()
    manifest = read_json(ROOT / "manifest.json")
    require(manifest["$schema"] == SCHEMA_URL, "Unexpected manifest schema URL")
    raw_schema = (ROOT / "schemas/MicrosoftTeams.schema.json").read_bytes()
    provenance = read_json(ROOT / "schemas/source.json")
    require(provenance["url"] == SCHEMA_URL, "Schema provenance URL differs")
    require(hashlib.sha256(raw_schema).hexdigest() == provenance["sha256"], "Pinned Microsoft schema digest differs")
    if args.download_schema:
        with urllib.request.urlopen(SCHEMA_URL, timeout=30) as response:
            fresh = response.read()
        require(hashlib.sha256(fresh).hexdigest() == provenance["sha256"], "Microsoft schema changed. Review and update the pinned copy.")
    schema = json.loads(raw_schema)
    formats = FormatChecker()

    @formats.checks("regex", raises=regex.error)
    def unicode_pattern(value):
        return not isinstance(value, str) or bool(regex.compile(value))

    def pattern(validator, expression, instance, schema):
        if isinstance(instance, str) and not regex.search(expression, instance):
            yield ValidationError("String does not match its schema pattern")

    def pattern_properties(validator, expressions, instance, schema):
        if isinstance(instance, dict):
            for expression, subschema in expressions.items():
                for key, value in instance.items():
                    if regex.search(expression, key):
                        yield from validator.descend(value, subschema, path=key, schema_path=expression)

    base = validators.validator_for(schema)
    # Microsoft's schema uses Unicode property escapes unsupported by Python re.
    base.check_schema(schema, format_checker=formats)
    validator = validators.extend(base, {"pattern": pattern, "patternProperties": pattern_properties})
    errors = list(validator(schema, format_checker=formats).iter_errors(manifest))
    if errors:
        # Do not print invalid values because a misplaced secret could be one.
        paths = ["/".join(map(str, error.absolute_path)) or "root" for error in errors]
        raise ValueError("Manifest schema validation failed at: " + ", ".join(paths))
    require(manifest["manifestVersion"] == "1.30", "Expected manifestVersion 1.30")
    require(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), "App version must have three numeric components")
    connectors = manifest["agentConnectors"]
    require(len(connectors) == 1, "Expected one fax connector")
    remote = connectors[0]["toolSource"]["remoteMcpServer"]
    require(remote["mcpServerUrl"] == "https://mcp.faxforagents.com/mcp", "Unexpected endpoint")
    require(remote["mcpToolDescription"] == {"file": "mcptools.json"}, "Unexpected tool definition path")
    auth = remote["authorization"]
    require(auth["type"] in {"ApiKeyPluginVault", "AzureKeyVault"}, "Review the selected authentication route before changing it")
    for filename in ("manifest.json", "mcptools.json", "review-cases.json"):
        raw = (ROOT / filename).read_text()
        require(not re.search(r"ffa_(?:test|live)_[A-Za-z0-9]{8,}", raw), f"Potential credential in {filename}")
        read_json(ROOT / filename)
    require(not re.search(r"Bearer\s+\S+|client_secret|access_token", auth["referenceId"], re.I), "Authorization reference must not contain a credential")
    tools = read_json(ROOT / "mcptools.json")["tools"]
    require(len(tools) == 17 and {t["name"] for t in tools} == EXPECTED, "Unexpected tool inventory")
    for tool in tools:
        require(bool(tool.get("description")), "Missing tool description")
        Draft202012Validator.check_schema(tool["inputSchema"])
        if "outputSchema" in tool:
            Draft202012Validator.check_schema(tool["outputSchema"])
    tool_source = read_json(ROOT / "schemas/tools-source.json")
    require(hashlib.sha256((ROOT / "mcptools.json").read_bytes()).hexdigest() == tool_source["mcptoolsSha256"], "Tool definitions differ from generated provenance")
    for key, size in (("color", (192, 192)), ("outline", (32, 32))):
        require(manifest["icons"][key] == ("Color.png" if key == "color" else "Outline.png"), "Unexpected icon path")
        with Image.open(ROOT / manifest["icons"][key]) as icon:
            require(icon.format == "PNG" and icon.size == size, f"Invalid {key} PNG dimensions")
            rgba = icon.convert("RGBA")
            if key == "outline":
                require(rgba.getchannel("A").getextrema() == (0, 255), "Outline must have transparent and opaque pixels")
                require(all((r, g, b) == (255, 255, 255) for r, g, b, a in rgba.get_flattened_data() if a), "Outline must be white")
            else:
                require(rgba.getchannel("A").getextrema() == (255, 255), "Color icon must be full bleed")
                rgb = rgba.convert("RGB")
                box = ImageChops.difference(rgb, Image.new("RGB", size, rgb.getpixel((0, 0)))).getbbox()
                require(box and box[0] >= 36 and box[1] >= 36 and box[2] <= 156 and box[3] <= 156, "Color brand mark exceeds the central 120x120 safe area")
    review = read_json(ROOT / "review-cases.json")
    cases = review["cases"]
    require(len(cases) == 8 and len({c["id"] for c in cases}) == 8, "Expected eight distinct review scenarios")
    require(sum(c["kind"] == "positive" for c in cases) == 5, "Expected five positive scenarios")
    require(sum(c["kind"] == "negative" for c in cases) == 3, "Expected three negative scenarios")
    for case in cases:
        require(case["prompt"] and case["expected_behavior"], "Review scenario lacks prompt or expectation")
        require(set(case["tools_triggered"].split(", ")) <= EXPECTED, "Review scenario names an unknown tool")
    for filename in ("intro.md", "README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md"):
        require((ROOT / filename).is_file(), f"Missing {filename}")
    listing = "\n".join([*manifest["description"].values(), connectors[0]["description"], (ROOT / "intro.md").read_text()])
    require(not re.search(r"\b(?:price|prices|pricing|free|paid|prepaid|cost|costs)\b|\$\d", listing, re.I), "Listing copy contains pricing language")
    require(";" not in listing, "Listing copy contains a semicolon")
    print("PASS: Microsoft v1.30 schema, 17 tool schemas, icons and eight review cases.")
    blockers = []
    if not auth["referenceId"].strip():
        blockers.append("authorization.referenceId is unset. Register credentials outside the repository.")
    if auth["type"] == "AzureKeyVault" and auth["referenceId"]:
        require(re.fullmatch(r"https://[a-zA-Z0-9-]+\.vault\.azure\.net/", auth["referenceId"]), "AzureKeyVault reference must be a vault URI, not a secret URI")
    if args.check_hosted or args.submission:
        spec = importlib.util.spec_from_file_location("generate_tools", ROOT / "scripts/generate-tools.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        hosted, _ = module.fetch_tools()
        if {t["name"]: t for t in hosted} != {t["name"]: t for t in tools}:
            blockers.append("Hosted tools/list differs from mcptools.json. Reconcile definitions before submission.")
    for blocker in blockers:
        print("PENDING: " + blocker)
    if (args.submission and blockers) or (args.check_hosted and any("tools/list" in b for b in blockers)):
        return 1
    print("Local validation passed. Microsoft host testing and certification remain operator work.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, StopIteration) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
