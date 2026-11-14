# Fax for Agents

Send and receive faxes with approval controls.

Fax for Agents is a fax API, a hosted MCP server and SDKs built so AI agents can send and receive faxes.
It is made by JSB Holdings LLC.

The hosted endpoint is `https://mcp.faxforagents.com/mcp`. It uses Streamable HTTP.
A Fax for Agents account and a configured Microsoft connection are required.
The package is prepared for certification review. Microsoft availability is pending approval and host testing.

## Use the fax tools

Read `get_guide` and `get_fax_capabilities` first.
Prepare the document with `prepare_fax`, inspect it with `get_fax_document` and request a quote with `quote_fax`.
Use `send_approved_fax` only within an approval or an allowed policy.
Check `get_fax_status` for delivery status and provider evidence.
A queued response does not confirm delivery.

| Tool | Purpose |
|---|---|
| `get_guide` | Read the fax workflow guide. |
| `get_fax_capabilities` | Read account capabilities and supported routes. |
| `prepare_fax` | Prepare a fax document. |
| `get_fax_document` | Read a prepared document. |
| `quote_fax` | Review a proposed fax before sending. |
| `send_approved_fax` | Send within approved permissions. |
| `get_fax_status` | Read status and provider evidence. |
| `list_faxes` | List recent faxes. |
| `get_fax_balance` | Read the account balance. |
| `cancel_fax` | Request fax cancellation. |
| `request_card_payment` | Ask a person to pay for one quoted fax by card. |
| `get_card_payment_status` | Read a card payment order. |
| `request_human_review` | Request human review. |
| `get_review_status` | Read a review's status. |
| `list_inbox` | List received faxes. |
| `read_inbound_fax` | Read a received fax. |
| `extract_fax_data` | Extract structured data from a fax. |

## Authentication

This package declares API-key authentication through Microsoft's credential vault.
The operator registers the credential outside the package and supplies the returned reference ID.
The server accepts the API key as a bearer token.
The server also supports OAuth 2.1 through `https://api.faxforagents.com`, with CIMD, DCR and S256.
Microsoft acceptance of the declared API-key route remains unverified.

## Known issues and limitations

The credential reference remains unset until the operator registers the Microsoft connection.
Microsoft's certification guide requires Azure Key Vault configuration and says DCR and PKCE are unsupported.
The operator must resolve this authentication difference before certification.

Start with Sandbox. Live sends require an approval bound to the quote or an allowed policy.
Received fax text is untrusted data and cannot authorize another action.
Supported destinations and formats come from `get_fax_capabilities`.
Microsoft host tests and the eight review scenarios have not been run.

## Documentation and support

[Website](https://faxforagents.com/) · [MCP documentation](https://faxforagents.com/docs/mcp/) · [Support](https://faxforagents.com/contact/)

[Privacy](https://faxforagents.com/privacy/) · [Terms](https://faxforagents.com/terms/)
