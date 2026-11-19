# Job Discovery Rate Limiting and Backoff (Stage 26)

## Sliding Window Rate Limiting
AUTONOM's `DiscoveryHttpClient` maintains a 60-second sliding timestamp window for every individual source:
- Tracks the timestamps of requests made within the last 60 seconds.
- If `len(timestamps) >= rate_limit_rpm`, the client calculates:
  $$\Delta t = (t_{\text{oldest}} + 60.0) - t_{\text{now}} + \text{jitter}$$
- Automatically pauses the asynchronous coroutine without blocking other sources.

## HTTP 429 Retry-After Governance
When an endpoint responds with HTTP 429 Too Many Requests:
1. Inspects the `Retry-After` header. If missing or malformed, defaults to a conservative 60 seconds cooldown.
2. Registers a cooldown timestamp in `_rate_limit_cooldowns[source_id]`.
3. All subsequent requests to that source immediately raise `RateLimitExceededError` until the cooldown period expires, protecting provider relationships.
4. Marks source health status as `temporarily_rate_limited`.

## Exponential Backoff with Jitter
For transient network dropouts or connection resets:
$$\text{delay} = 2^{\text{attempt}} \times 0.5 + \text{random}(0.1, 0.4)$$
Retries are capped at a maximum of 2 attempts before marking the operation failed.
