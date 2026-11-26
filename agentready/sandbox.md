# Sandbox and test access

Goal: let an agent builder test the full tool flow without real funds.

Available today, no setup:
- Market tools (`list_chains`, `search_tokens`, `trending_tokens`, `price_history`, `quote_swap`, `swap_status`) need no credential and move no funds. Use them to test discovery, parsing and error handling.
- `prepare_swap` builds a swap and never broadcasts; the person signs. A key limited to "Prepare swaps" cannot spend.
- Set a small daily budget and per-trade cap in Agent access before testing `execute_swap`.

Needs a build by the server owners (not in this repo):
- A test credential at `https://tokens.wardenprotocol.org/mcp/sandbox` (or a `Warden-Env: sandbox` header) that returns fixed sample data for `get_wallet`, `agent_permissions`, `prepare_swap`, `execute_swap` and `swap_status`, and never signs or sends.
- Sample tokens named "Sample Token" only, with no link to real tokens.

Link this page from `/mcp` and from the `sandbox` field of the server card.
