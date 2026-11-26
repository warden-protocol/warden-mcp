# Security policy

## Report a vulnerability

Email **support@wardenprotocol.org** with the subject line `Security: Warden MCP`.

Please include:

- What you found and where (tool name, endpoint or URL)
- Steps to reproduce
- What an attacker could do with it

Do not open a public GitHub issue for a security report, and do not test against wallets or funds that are not yours.

We confirm every report we receive and investigate it with care. We tell you when it is fixed.

## Scope

- The remote MCP server at `https://tokens.wardenprotocol.org/mcp`
- Its OAuth endpoints under `https://tokens.wardenprotocol.org/oauth/` and `/.well-known/`
- The manifests and config files in this repository

## How the server protects wallets

See the [Security section of the README](README.md#security).
