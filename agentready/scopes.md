# Scopes per wallet tool

Uses the four scope names the server already publishes in `/.well-known/oauth-protected-resource` and `/.well-known/oauth-authorization-server`: `read`, `launch`, `swap`, `trade`. No new names are introduced. The tool mapping below is a proposal for product review.

| Tool | Needs | Proposed scope |
|---|---|---|
| list_chains, search_tokens, trending_tokens, price_history, quote_swap, swap_status | nothing | none |
| get_wallet | credential | `read` |
| agent_permissions | credential | `read` |
| session_request_status | credential | `read` |
| request_session | credential | `trade` (asks the person to open a session) |
| prepare_swap | credential + "Prepare swaps" | `swap` (builds a swap the person signs) |
| execute_swap | credential + open session | `trade` (signs and sends within session limits) |
| token launch (app only, not an MCP tool) | credential | `launch` |

Rules:
- A `trade` grant still needs an open hands-free session and passes the budget and per-trade checks. A scope never replaces them.
- A call without the needed scope returns HTTP 403, `WWW-Authenticate: Bearer error="insufficient_scope", scope="<scope>", resource_metadata="..."` and the JSON error `insufficient_scope`.
- `wk_` keys carry the scopes the owner ticked in Portfolio, Agent access.

Open for product review: whether `request_session` belongs under `swap` or `trade`, and whether `session_request_status` needs `read` or none.
