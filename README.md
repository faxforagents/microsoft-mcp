<p align="center">
  <a href="https://faxforagents.com"><img src="Color.png" width="88" alt="Fax for Agents"></a>
</p>

<h1 align="center">Fax for Agents for Microsoft Copilot</h1>

<p align="center">Send and receive faxes with approval controls.</p>

<p align="center">
  <a href="https://faxforagents.com">Website</a> ·
  <a href="https://faxforagents.com/docs/quickstart/">Quickstart</a> ·
  <a href="https://faxforagents.com/docs/api/">API reference</a> ·
  <a href="https://faxforagents.com/docs/sdks/">SDKs</a> ·
  <a href="https://faxforagents.com/mcp/">MCP</a> ·
  <a href="https://app.faxforagents.com">Dashboard</a> ·
  <a href="https://faxforagents.com/pricing/">Pricing</a> ·
  <a href="https://faxforagents.com/changelog/">Changelog</a> ·
  <a href="https://faxforagents.com/affiliates/">Affiliate program</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-1f6feb" alt="MIT licence"></a>
  <a href="https://faxforagents.com/mcp/"><img src="https://img.shields.io/badge/MCP-17%20tools-6b4fbb" alt="17 MCP tools"></a>
</p>

Fax for Agents is a fax API, a hosted MCP server and SDKs built so AI agents can send and receive faxes.
It is made by JSB Holdings LLC.

This repository prepares a remote MCP package for Microsoft's certification preview.
It targets Microsoft 365 Copilot and Copilot Studio, subject to Microsoft's acceptance and host testing.
It has not been submitted or certified.

## Validate locally

Use Python 3 with the dependencies in [scripts/requirements.txt](scripts/requirements.txt).

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
PYTHON=.venv/bin/python sh scripts/validate.sh
```

The validator checks the downloaded Microsoft v1.30 JSON schema, tool schemas, file references, icon dimensions and eight review scenarios.
It also checks white outline pixels, transparency and the color icon's central 120x120 safe area.
Local validation permits the unset credential reference and reports it as pending.
It does not establish Microsoft host compatibility or certification readiness.

```bash
PYTHON=.venv/bin/python sh scripts/validate.sh --download-schema
PYTHON=.venv/bin/python sh scripts/validate.sh --submission
```

The first command compares a fresh schema download with the pinned copy.
The second rejects an unset reference and differences between hosted and packaged tools.
It currently fails for both reasons.

## Package contents

| File | Purpose |
|---|---|
| [manifest.json](manifest.json) | Microsoft v1.30 app manifest with `agentConnectors` and `remoteMcpServer`. |
| [mcptools.json](mcptools.json) | Seventeen tool definitions in a `tools` array. |
| [intro.md](intro.md) | Public server documentation and limitations. |
| [Color.png](Color.png) | 192x192 full color icon with the brand mark inside the 120x120 safe area. |
| [Outline.png](Outline.png) | 32x32 white outline icon on a transparent background. |
| [review-cases.json](review-cases.json) | Five positive and three negative scenarios adapted from the ChatGPT package. |
| [schemas/source.json](schemas/source.json) | Download URL, date and digest for Microsoft's schema. |
| [schemas/tools-source.json](schemas/tools-source.json) | Definition source and digest for the generated tool file. |

The app GUID was generated locally for this package. It is not evidence of a registered Microsoft offer.
Keep it stable when registering the app, or replace it with the operator's established app ID before testing.
The schema defines `developer.websiteUrl` as the support page, so it points to our contact page.
The schema rejects the certification example's `developer.contactInfo` field. Support contact details belong in the operator's listing configuration.

## Current submission blockers

The [certification overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-certification) requires Azure Key Vault configuration.
Its FAQ says DCR and PKCE are unsupported.
Fax for Agents uses OAuth 2.1 with S256, CIMD and DCR, and also accepts API keys as bearer tokens.
The authorization server is `https://api.faxforagents.com`.

The [remote MCP configuration guide](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/configure-plugin-mcp-servers) documents `ApiKeyPluginVault` for `agentConnectors`.
The downloaded v1.30 schema accepts that type.
This package declares that API-key route because it matches the existing server authentication.
Microsoft must confirm its acceptance for this certification intake and both target hosts.
Do not infer acceptance from schema validation.

The generator used `../mcp/src/tool-definitions.json` without rewriting any tool definitions.
On 2026-11-14 the 17 definitions equal the `tools/list` of the hosted server at version 1.20.3.
`send_approved_fax` and `cancel_fax` carry `destructiveHint` true.
Regenerate before submission if the hosted server changes.

No reviewer credentials or Microsoft tenant were available for functional testing.
Every review scenario remains `not_run`.

## Secret configuration

For the declared API-key route, follow the [remote MCP guide](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/configure-plugin-mcp-servers#use-api-key-authentication).
Register the credential in [Developer Portal](https://dev.teams.microsoft.com/) and copy the returned registration ID into `authorization.referenceId`.
That field is intentionally empty in the source manifest. It must never contain the credential itself.

The linked [API-key guide](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-authentication-api-key#use-the-teams-developer-portal) describes Tools > API key registration.
Choose Create an API key or New API key, then Add secret.
Complete the registration name, base URL, target tenant and target Teams app, then save.
Confirm the MCP-specific base URL and `Authorization: Bearer` delivery with Microsoft before registration.
The API-key guide describes OpenAPI plugins, while the remote MCP guide supplies the authority for using that registration with `agentConnectors`.
Do not add guessed header fields to the manifest or package an OpenAPI plugin as a substitute.

Use a dedicated Sandbox reviewer credential with only the scopes needed for the review.
Share reviewer access through the private Microsoft review process.
A sandbox key is free. Live sends are prepaid.
Those operational facts are excluded from the manifest descriptions and public introduction.

### Azure Key Vault certification procedure

The [certification FAQ](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-certification#how-can-i-set-up-the-key-vault) gives this procedure.
This procedure identifies the vault by its URI.

1. Create an Azure Key Vault in your Azure tenant through the Azure portal.
2. Store `ClientId`, `ClientSecret` and `TokenUrl` as secrets.
3. Add `AuthorizationUrl` for an OAuth2 identity provider. Add `RefreshUrl` and `Scopes` when the provider configuration needs them.
4. For an AAD identity provider, add `AzureActiveDirectoryResourceId`.
5. Create a service principal for Microsoft application `8e91e74f-afe9-41cd-8c3f-17a9562a74ea`.
6. Grant that principal `Key Vault Secrets User` or equivalent RBAC read access to the vault.
7. Set `authorization.type` to `AzureKeyVault`. Set `authorization.referenceId` to the vault URI, not a secret URI.
8. Package and submit after configuration and testing.

Secret names are case-sensitive. The FAQ defines these provider-specific sets.

| Identity provider | Required secrets |
|---|---|
| OAuth2 | `ClientId`, `ClientSecret`, `AuthorizationUrl`, `TokenUrl` |
| OAuth2 with refresh token | `ClientId`, `ClientSecret`, `AuthorizationUrl`, `TokenUrl`, `RefreshUrl` |
| OAuth2 with scopes | Add `Scopes` to the OAuth2 set. |
| Azure AD | `ClientId`, `ClientSecret`, `TokenUrl`, `AzureActiveDirectoryResourceId` |

The [public discovery document](https://api.faxforagents.com/.well-known/oauth-authorization-server) reports `https://api.faxforagents.com/oauth/authorize` and `https://api.faxforagents.com/oauth/token`.
It advertises S256 and refresh-token grants.
Obtain actual client configuration through an agreed registration flow.
The fetched certification guide does not establish a compatible S256 flow or an API-key secret layout for its Azure Key Vault path.
Resolve that with Microsoft before replacing the declared authentication type.
Do not disable PKCE to make this package fit the preview.

## Partner Center steps for the operator

1. Sign in with the company's Microsoft Entra work account at [Partner Center](https://partner.microsoft.com/dashboard).
   Complete JSB Holdings LLC's business verification and enroll in Microsoft 365 and Copilot.
   Follow the [enrollment guide](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/open-a-developer-account).
   Existing partners use Settings > Account settings > Programs > Microsoft 365 and Copilot > Get Started.
   Account owners must accept the applicable agreements and provide the real legal business details.
2. Submit the [MCP certification intake](https://forms.cloud.microsoft/pages/responsepage.aspx?id=v4j5cvGGr0GRqy180BHbR9r8NB1yEjBHvyRFUGv3hYVUQUc3WkpTSDNYSzFTRTNXRThBMUtFWkwyMi4u&route=shorturl).
   Microsoft supplies further instructions if it picks up the preview submission.
   Confirm endpoint ownership and disclose the authentication compatibility issue.
3. Follow Microsoft's instructions for the `Apps and Agents for M365 and Copilot` offer type.
   The [certification page](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-certification#whats-changing) names that type for new MCP submissions.
   Do not substitute the separate REST connector offer from research E04 or create the declarative agent from E05.
4. Configure the accepted authentication route, reconcile hosted definitions and run all eight scenarios in the target tenant.
   Verify bearer delivery, credential revocation and account isolation for the API-key route.
   Capture actual results and reviewer setup instructions privately.
5. Run local submission checks and [Developer Portal package validation](https://dev.teams.microsoft.com/).
   Follow the [remote MCP validation steps](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/configure-plugin-mcp-servers#validate-and-test-your-plugin) for both intended hosts.
6. Prepare the approved archive with `manifest.json`, `mcptools.json`, `Color.png`, `Outline.png` and `intro.md` at its root.
   Provide `review-cases.json` as supporting reviewer instructions when Microsoft requests them.
   Exclude `.coding-agent`, credentials, local environments and schema tooling.
7. Complete listing metadata with the manifest descriptions, JSB Holdings LLC publisher details, support, privacy and terms links.
   Supply any additional assets and reviewer access requested for the selected offer.
   Submit through the accepted intake instructions and address Microsoft's validation findings.
8. Confirm approval and supported distribution surfaces before announcing availability.
   Resubmit changes to tools, significant metadata or certified behavior through Microsoft's update process.

The certification page calls `intro.md` required in its package table and optional later. This package includes it.
The legacy route remains documented through November 18, 2026. Use it only if Microsoft confirms that route for this submission.
The [Marketplace publication guide](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/publish-plugin-publicly) requires eligibility for the selected offer type.
Successful local validation does not establish that eligibility.

## Regenerate tools and icons

```bash
python3 scripts/generate-tools.py --source ../mcp/src/tool-definitions.json
python3 scripts/generate-tools.py
.venv/bin/python scripts/make-icons.py .coding-agent/avatar-512.png
```

Choose one tool-generation command. The second contacts the public hosted endpoint and performs initialization followed by `tools/list`.
It sends no credentials and executes no tools. It rejects unexpected tool names before writing output.
The first uses the permitted local mirror.
The icon command needs the original supplied logo, which is excluded from version control under `.coding-agent`.
Keep source tool descriptions intact, including operational billing vocabulary. They are protocol definitions, separate from listing copy.

## Licence

MIT. See [LICENSE](LICENSE).
Microsoft's downloaded schema retains its upstream notices and provenance.
Report security issues to security@faxforagents.com. See [SECURITY.md](SECURITY.md).
