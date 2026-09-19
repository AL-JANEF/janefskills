---
name: database-integrity
description: >-
  Schema design, migrations, transactions, indexes, query behavior, backfills,
  and tenant isolation or RLS. Treats every schema or migration change as high
  risk because deployed data already exists. Use for SQL, ORMs, data models,
  migration strategy, query performance, or data-integrity questions.
license: MIT
---

# Database Integrity

Schema and migration changes are high risk because deployed data already exists and cannot be re-run. Put durable invariants in constraints when the database can enforce them.

## Model and invariants

- Choose types, nullability, defaults, keys, and uniqueness from domain meaning, not sample data.
- Preserve constraints, foreign keys, uniqueness, nullability semantics, transactions, and least privilege.
- Make tenant or ownership boundaries explicit in every access path. In multi-tenant systems a missing tenant scope is a critical finding; where RLS exists, never bypass it with a privileged role to make a query work.

## Queries and transactions

- Parameterize every query. Treat ORM convenience as syntax, not proof of correct query count or transaction behavior.
- Inspect plans with representative cardinality before adding indexes; account for write amplification and maintenance cost.
- Keep transactions short; define isolation needs and lock ordering for concurrent writes.
- Avoid N+1 access and unbounded reads; paginate with stable ordering.

## Migrations

- Design expand → migrate → contract phases for mixed application versions.
- Separate schema change, backfill, validation, and cleanup when locks or data volume matter. Backfills need batching, idempotent retries, progress tracking, and production-load awareness.
- Make migrations deploy-compatible, observable, and recoverable; define rollback or forward-fix.
- Destructive migrations (drop, truncate, type narrowing, data deletion) require explicit authorization and staging. Never claim one is safe without backup and restore evidence appropriate to the environment.
- Audit-log sensitive data changes (`security-logging`).

## Verification

- Apply the migration from zero and against representative data; run representative queries afterwards.
- Test constraints, concurrent edge cases, upgrade and rollback/forward-fix paths.
- Confirm explain plans and lock impact for performance-sensitive production queries.
- For RLS, tenant scoping, or privilege changes: run a real database check that a cross-tenant or unprivileged access is denied, and show that removing the control makes that test fail.
