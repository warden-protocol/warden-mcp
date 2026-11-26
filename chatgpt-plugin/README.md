# ChatGPT plugin package

Source for the Warden Token Terminal listing in the ChatGPT plugin directory.
The plugin wraps one remote MCP server, the read-only endpoint at
`https://tokens.wardenprotocol.org/mcp/directory` (no sign-in).

Tools it exposes: `list_chains`, `search_tokens`, `trending_tokens`,
`price_history`, `quote_swap`, `swap_status`. None of them signs, moves funds
or places trades.

## Layout

```
chatgpt-plugin/
  plugin/              files that go into the ZIP, at its root
    plugin.json        Agent Plugins manifest with the OpenAI listing, review cases and release notes
    mcp.json           the one remote MCP server
    assets/logo.png    512x512 primary icon
    assets/icon.png    256x256 composer icon
  source-icon.png      original 912x912 icon from tokens.wardenprotocol.org/warden-icon.png
  build.py             validates the package and writes dist/warden-token-terminal-chatgpt-plugin.zip
```

## Build

```sh
python3 chatgpt-plugin/build.py          # validate and build the ZIP
python3 chatgpt-plugin/build.py --check  # validate only
```

`build.py` checks the limits in the OpenAI docs (name format, 30-character
display name and subtitle, the four HTTPS listing URLs, square PNG icons,
five positive and three negative review cases, one MCP server, no headers, no
credentials or hooks). With `jsonschema` installed it also validates both files
against the published Agent Plugins 1.0.0 schemas.

Docs used (read 26 Nov 2026):

- Package guide: https://developers.openai.com/plugins/build/plugins
- Manifest fields: https://developers.openai.com/plugins/deploy/submission#manifest-fields
- Review rules: https://developers.openai.com/plugins/deploy/app-review
- Guidelines: https://developers.openai.com/plugins/plugin-guidelines

## Not in the ZIP

Reviewer credentials are not needed (no sign-in). The demo video URL is
entered in the dashboard under Review details, so it is not set here.
