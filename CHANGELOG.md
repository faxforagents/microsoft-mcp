# Changelog

## Unreleased

`mcptools.json` holds 17 tool definitions. The hosted server added `request_card_payment` and `get_card_payment_status` on 2026-11-12.
The generator and the validator expect 17 tools.

`mcptools.json` was regenerated on 2026-11-14 and equals the hosted `tools/list` at version 1.20.3.
`send_approved_fax` and `cancel_fax` now carry `destructiveHint` true. They carried false.
The text of `quote_fax` and `read_inbound_fax` follows the hosted server.
The README and the intro no longer say the hosted server names the document tool `get_document`. It has named it `get_fax_document` since 1.8.0.

## 0.1.0 (2026-11-04)

Prepared the Microsoft remote MCP package with 15 tool definitions and eight review scenarios.
Added Microsoft schema validation and both package icons.
Documented authentication, business verification and the remaining submission blockers.
