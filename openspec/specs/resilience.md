# Resilience Specification

## Goals
Ensure reliable service under upstream fluctuations via timeouts, retries, fallbacks, and circuit breakers.

## Timeouts (Settings)
- PRO_TIMEOUT: default 60s
- FLASH_TIMEOUT: default 20s
- FLASH_LITE_TIMEOUT: default 10s
- LEGACY_FLASH_TIMEOUT: default 15s

## Retries
- Use `tenacity` with exponential backoff for transient upstream errors (timeouts, 5xx, rate limits).
- Cap max attempts per model to bound latency.

## Fallbacks
- If a targeted model fails or times out, automatically route to the next tier:
  - pro → flash → flash-lite → 2.0-flash
- Preserve contextual state across retries and fallbacks.

## Circuit Breaker
- Use `pybreaker` to trip on consecutive failures per model.
- While open, short-circuit requests to healthier models.
- Half-open probes to restore service when upstream recovers.

## Observability (Planned)
- Structured logs with correlation ids (request id, client key hash).
- Metrics: request count, error rate, latency per model, breaker state.
- Traces: triage → dispatch → tool exec chain.
