# Tool error format

Every tool error returns `isError: true` and a JSON body in both `content[0].text` and `structuredContent`:

```json
{
  "error": {
    "code": "invalid_arguments",
    "message": "chainId: expected number, received undefined",
    "retryable": false
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `code` | string | Stable machine-readable code from the table below |
| `message` | string | One plain sentence an agent can show the person |
| `retryable` | boolean | `true` if the same call may succeed later without changes |
| `retryAfterSeconds` | integer, optional | Wait before retrying; present when `retryable` is true and the wait is known |

| Code | retryable | When |
|---|---|---|
| `invalid_arguments` | false | Input failed validation (today: plain text "Input validation error: ...") |
| `unauthorized` | false | No or invalid credential. HTTP 401 with `WWW-Authenticate` |
| `insufficient_scope` | false | Credential lacks the scope for this tool. HTTP 403 with `WWW-Authenticate` naming the scope |
| `needs_human` | false | The person must sign or approve; hand the prepared transaction back |
| `session_required` | false | `execute_swap` without an open hands-free session; call `request_session` |
| `limit_exceeded` | false | Daily budget or per-trade cap would be passed |
| `not_found` | false | Unknown token, chain or swap id |
| `no_liquidity` | true | No route right now; try again or a smaller amount |
| `rate_limited` | true | Too many calls; honour `retryAfterSeconds` |
| `upstream_unavailable` | true | A data or routing provider failed |
| `internal_error` | true | Unexpected server error |

HTTP-level failures (401, 403, 429) keep their status and add the same JSON body.
