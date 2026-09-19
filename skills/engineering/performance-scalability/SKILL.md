---
name: performance-scalability
description: >-
  Measure first, then fix latency, throughput, memory, CPU, bundle size, query
  count, contention, and scaling problems with before/after evidence under the
  same workload. Use for anything slow, expensive, or expected to scale; never
  optimize from intuition or trade correctness for speed silently.
license: MIT
---

# Performance & Scalability

Measure first. Averages hide tail pain, intuition hides the real hot path, and a synthetic microbenchmark does not prove production improvement.

## Measure

- Define the user-visible metric, workload, percentile (p95/p99), environment, and acceptable threshold before editing.
- Reproduce with representative data; isolate measurement noise; profile the dominant resource and trace the critical path.
- Frontend: bundle size, render work, media loading, layout stability, interaction latency. Backend: tail latency, saturation, queue growth, lock contention, database pressure, connection pools, downstream limits.

## Optimize

- Remove unnecessary work before caching, parallelizing, or changing infrastructure.
- Fix algorithmic or query complexity (N+1, unbounded reads, missing indexes) before micro-optimizing syntax.
- Bound caches by memory, lifetime, invalidation, and tenant/security scope. A cache that leaks across tenants is a security defect, not a performance win.
- Treat concurrency as a trade-off involving contention, rate limits, ordering, and failure amplification.
- Preserve readability unless the measured gain justifies complexity and tests protect it. Do not trade correctness, durability, or consistency for speed without an explicit, recorded decision.

## Verify

- Compare before and after under the same workload; report variance, not only the best run.
- Check correctness, cold/warm behavior, resource transfer (did the cost move elsewhere?), and regression on adjacent workloads.
- Use realistic load profiles for critical paths; distinguish capacity, endurance, spike, and recovery testing.
- Add a budget or benchmark gate only when the environment is stable enough to produce actionable failures.

## Output

```
## Performance: <path>
Baseline: <metric> = <value> (p95/p99, workload, N runs, variance)
Cause: <dominant resource / hot path with evidence>
Change: <what and why>
After: <metric> = <value> (same workload)
Not covered: <e.g. production traffic mix, cold cache>
```
