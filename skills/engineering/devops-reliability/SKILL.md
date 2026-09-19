---
name: devops-reliability
description: >-
  CI/CD pipelines, containers, infrastructure as code, cloud services and IAM,
  deployment and rollout strategy, rollback, backups and restore, monitoring
  and alerting, and reliability controls. Use for any workflow, Dockerfile,
  Terraform, Kubernetes, cloud, deployment, or operations change. Production
  and infrastructure mutations require explicit authorization.
license: MIT
---

# DevOps, Cloud & Reliability

Production and infrastructure mutations are never assumed to be authorized. Validate first, mutate only with explicit approval, and keep a rollback.

## Build and supply chain

- Reproducible builds from declared inputs; pin tools, actions, and base images; review third-party automation before adopting it.
- Minimal, non-root runtime images; build credentials never in layers or logs.
- Build an artifact once and promote it across environments instead of rebuilding per environment.

## Delivery

- Separate validation from mutation: plan, dry-run, lint, or diff before any apply or deploy.
- Define health checks, readiness/liveness, rollout strategy, rollback, and database compatibility before changing production behavior.
- CI gates fail meaningfully; never convert a real failure into a warning, mask exit codes, or continue after a partial critical step.
- Environment-specific values live in configuration, not divergent branches. No snowflake manual state.
- Serialize or isolate deployments that mutate shared state.

## Cloud and IAM

- Workload identity and short-lived credentials; scope IAM to required actions and resources; least privilege for CI identities.
- Private connectivity by default; restrict ingress and egress; encrypt in transit and at rest with explicit key ownership and rotation.
- Separate accounts/projects and blast radius by environment and data sensitivity.
- Record quotas, regional availability, failure modes, egress, and pricing dimensions before committing to a managed service.

## Operations

- Define SLOs, backups, restore tests, RPO/RTO, capacity, and failover. Replication is not a backup; a backup without a verified restore is incomplete.
- Alerts have an owner, a user impact, and an actionable runbook. Bound logs and artifacts; keep secrets and personal data out (`secrets-guard`, `security-logging`).
- Timeouts, bounded retries, circuit breaking or backpressure, and resource limits where saturation is possible.

## Verification

Syntax and schema validation of workflows, IaC, and container files; a non-mutating plan or dry-run; failure propagation checked; rollback exercised on the closest safe environment. Report which of these ran and which could not.
