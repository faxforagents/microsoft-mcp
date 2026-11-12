#!/usr/bin/env python3
"""Export public MCP definitions without credentials or tool execution."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://mcp.faxforagents.com/mcp"
EXPECTED = set("get_guide get_fax_capabilities prepare_fax get_fax_document quote_fax send_approved_fax get_fax_status list_faxes get_fax_balance cancel_fax request_card_payment get_card_payment_status request_human_review get_review_status list_inbox read_inbound_fax extract_fax_data".split())


def fetch_tools():
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    def rpc(method, params=None, request_id=None):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        if request_id is not None:
            message["id"] = request_id
        request = urllib.request.Request(ENDPOINT, json.dumps(message).encode(), headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            session = response.headers.get("Mcp-Session-Id")
            if session:
                headers["Mcp-Session-Id"] = session
            body = response.read().decode()
            if request_id is None:
                return None
            if "text/event-stream" in response.headers.get("Content-Type", ""):
                messages = []
                for event in body.replace("\r\n", "\n").split("\n\n"):
                    data = "\n".join(line[5:].lstrip() for line in event.splitlines() if line.startswith("data:"))
                    if data:
                        messages.append(json.loads(data))
                result = next(item for item in messages if item.get("id") == request_id)
            else:
                result = json.loads(body)
            if "error" in result:
                raise RuntimeError(f"{method} returned an MCP error")
            return result["result"]

    initialized = rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "faxforagents-microsoft-package", "version": "1.0.0"}}, 1)
    headers["MCP-Protocol-Version"] = initialized["protocolVersion"]
    rpc("notifications/initialized")
    tools = []
    cursor = None
    seen = set()
    while True:
        page = rpc("tools/list", {"cursor": cursor} if cursor else {}, 2 + len(seen))
        tools.extend(page["tools"])
        cursor = page.get("nextCursor")
        if not cursor:
            break
        if cursor in seen:
            raise RuntimeError("Repeated tools/list cursor")
        seen.add(cursor)
    return tools, {"source": ENDPOINT, "method": "initialize, notifications/initialized, tools/list", "protocolVersion": initialized["protocolVersion"], "serverInfo": initialized["serverInfo"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Use the sibling MCP tool-definitions.json mirror")
    args = parser.parse_args()
    if args.source:
        raw = args.source.read_bytes()
        tools = list(json.loads(raw)["tools"].values())
        provenance = {"source": str(args.source), "sourceSha256": hashlib.sha256(raw).hexdigest(), "method": "local hosted-definition mirror"}
    else:
        tools, provenance = fetch_tools()
    if len(tools) != 17 or {tool["name"] for tool in tools} != EXPECTED:
        raise RuntimeError("Tool inventory changed. Review before generating a package.")
    output = (json.dumps({"tools": tools}, indent=2, ensure_ascii=True) + "\n").encode()
    (ROOT / "mcptools.json").write_bytes(output)
    provenance["mcptoolsSha256"] = hashlib.sha256(output).hexdigest()
    (ROOT / "schemas/tools-source.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print("Generated mcptools.json with 17 unmodified tool definitions.")


if __name__ == "__main__":
    main()
