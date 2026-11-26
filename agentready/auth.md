# Warden Token Terminal: agent authentication

Served at `https://tokens.wardenprotocol.org/.well-known/auth.md`.

## Summary
Market tools need no credential. Wallet tools act for the wallet whose owner connected the agent, by OAuth sign-in or a `wk_` key sent as `Authorization: Bearer`.

## Sign in with OAuth 2.1
- Resource: `https://tokens.wardenprotocol.org/mcp`
- Protected resource metadata: `https://tokens.wardenprotocol.org/.well-known/oauth-protected-resource/mcp`
- Authorization server: `https://tokens.wardenprotocol.org` (metadata at `/.well-known/oauth-authorization-server`)
- Authorization: `/oauth/authorize`, token: `/oauth/token`, registration: `/oauth/register`
- PKCE S256 required. Public clients. Client ID metadata documents and dynamic registration supported.
- On a 401 the server sends `WWW-Authenticate: Bearer resource_metadata="<protected resource metadata URL>", authorization_uri="https://tokens.wardenprotocol.org"`, so a client finds the authorization server without reading this page.

## Create a key
1. The wallet owner signs in at https://tokens.wardenprotocol.org.
2. Portfolio, Agent access, Connect your agent.
3. Choose the permissions and limits, copy the setup message or the `wk_` key.
4. The agent keeps the key in the environment variable `WARDEN_TOKEN` and sends `Authorization: Bearer $WARDEN_TOKEN`.
5. The owner can revoke keys in Agent access at any time.

## Scopes
`read`, `swap`, `trade`, `launch`. Per-tool mapping: see scopes.md in this folder (to be published with this file after product review).

## Hands-free trading
`execute_swap` also needs an open session. The agent calls `request_session`, gives the person the returned link and code, then polls `session_request_status`. Budgets and per-trade caps are checked on the server for every trade.

## Errors
`unauthorized` (401), `insufficient_scope` (403). Body format: see errors.md.

## Sandbox
See sandbox.md.
