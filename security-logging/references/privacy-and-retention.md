# Privacy and Retention

Security logs must be useful without becoming a permanent collection of personal
data. Treat IP addresses, user identifiers, device identifiers, and location as
sensitive operational data even when they are not application secrets.

## Minimize

- Record only fields needed for a defined detection or investigation use case.
- Prefer stable internal actor IDs over names or email addresses.
- Truncate or pseudonymize IP addresses when exact values are unnecessary.
- Do not copy request bodies or database records into audit events.

## Retain deliberately

Set a documented retention period based on incident-response needs and applicable
legal requirements. Apply shorter retention to high-volume or more identifying
telemetry. Expire data automatically; an unwritten "keep forever" policy is not a
policy.

## Restrict and audit access

Limit log access to operational roles that need it, record access to sensitive
audit data, encrypt transport and storage, and separate production logs from
developer-facing diagnostics.

## Verify

Sample emitted events and confirm that sensitive fields are absent or minimized.
Test retention deletion and access controls rather than relying on configuration
screenshots alone.
