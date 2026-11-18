# Changelog

## Unreleased

`mcptools.json` holds 17 tool definitions. The hosted server added `request_card_payment` and `get_card_payment_status` on 2026-11-12.
The generator and the validator expect 17 tools.

`mcptools.json` was regenerated on 2026-11-14 and equals the hosted `tools/list` at version 1.20.3.
`send_approved_fax` and `cancel_fax` now carry `destructiveHint` true. They carried false.
The text of `quote_fax` and `read_inbound_fax` follows the hosted server.
The README and the intro no longer say the hosted server names the document tool `get_document`. It has named it `get_fax_document` since 1.8.0.

`mcptools.json` was regenerated on 2026-11-15 from `../mcp/src/tool-definitions.json`. It equals the hosted `tools/list` with the tools of API 1.20.6, output schemas aside.
Every input schema now says `additionalProperties: false`. The hosted server refuses an argument a tool does not list since API 1.20.5.
The description of `get_fax_capabilities` says that `me.scopes` is what the credential is allowed to do and `capabilities.scopes` is every scope there is.

`mcptools.json` was regenerated again on 2026-11-15 from `../mcp/src/tool-definitions.json`. It equals the hosted `tools/list` at version 1.20.9, output schemas aside.
The description of `request_card_payment` says the card is held at payment, not authorized. It states the payment rule of API 1.20.9 too. A failed fax costs nothing, and a fax that stops part way costs the price of the pages that arrive.
Nothing else in the 17 definitions changed since 1.20.6.

`mcptools.json` was regenerated at hosted version 1.20.10 from `../mcp/src/tool-definitions.json` of faxforagents/mcp 0.5.6. It came out byte for byte the same.
API 1.20.10 changed no name, title, description, input schema or annotation of the 17 tools. It changed the output schema of `quote_fax`, the guide and three answer texts, and the package carries none of them.
The definitions equal the hosted `tools/list` of 2026-11-15 at version 1.20.10, output schemas aside.

`mcptools.json` was regenerated at hosted version 1.21.12 from `../mcp/src/tool-definitions.json` of faxforagents/mcp 0.5.8.
`request_card_payment` now carries `destructiveHint` true. Once a person pays, the fax goes out and cannot be taken back.
The description of `get_fax_capabilities` says it returns the credential's environment and scopes. It said account identity.
API 1.21.11 and 1.21.12 also cut every tool's answer to an allow-list. The package carries no answers and no output schemas, so nothing else changed.
The definitions equal the hosted `tools/list` of 2026-11-18 at version 1.21.12, output schemas aside.

## 0.1.0 (2026-11-04)

Prepared the Microsoft remote MCP package with 15 tool definitions and eight review scenarios.
Added Microsoft schema validation and both package icons.
Documented authentication, business verification and the remaining submission blockers.
