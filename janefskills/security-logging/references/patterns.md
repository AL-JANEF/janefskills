# Logging & Detection Patterns

Copyable structures for audit logging, redaction, and detection.

## Audit log entry structure

A consistent, structured (JSON) entry makes logs queryable and useful for
reconstruction:

```js
function auditLog(event) {
  logger.info({
    ts: new Date().toISOString(),   // UTC
    actor: event.userId,            // id, not full PII
    action: event.action,           // 'login.failure', 'record.update', 'role.grant'
    target: event.target,           // what was affected (record id, user id)
    source: {
      ip: event.ip,
      requestId: event.requestId,
    },
    outcome: event.outcome,         // 'success' | 'failure' | 'denied'
    // for mutations, a diff makes the entry genuinely useful:
    changes: event.changes,         // { field: { from, to } } — already redacted
  });
}
```

Example calls:
```js
auditLog({ userId: u.id, action: 'login.failure', target: u.id,
           ip, requestId, outcome: 'failure' });

auditLog({ userId: admin.id, action: 'role.grant', target: target.id,
           ip, requestId, outcome: 'success',
           changes: { role: { from: 'member', to: 'admin' } } });
```

## Redaction before logging

Strip sensitive fields before anything is written:

```js
const REDACT = ['password', 'token', 'authorization', 'cookie',
                'secret', 'apiKey', 'cardNumber'];

function redact(obj) {
  const out = Array.isArray(obj) ? [] : {};
  for (const [k, v] of Object.entries(obj)) {
    if (REDACT.includes(k)) out[k] = '[REDACTED]';
    else if (v && typeof v === 'object') out[k] = redact(v);
    else out[k] = v;
  }
  return out;
}

logger.info(redact(payload));
```

Mask rather than drop when a fragment aids debugging:
```js
const masked = card.slice(0, 6) + '******' + card.slice(-4);
```

## Detection: failed-login threshold

```js
// Count recent failures per account; alert + throttle past a threshold.
async function onLoginFailure(userId, ip) {
  const key = `login_fail:${userId}`;
  const count = await store.incr(key);
  if (count === 1) await store.expire(key, 15 * 60);   // 15-min window
  if (count >= 5) {
    auditLog({ userId, action: 'login.bruteforce_suspected', target: userId,
               ip, outcome: 'denied' });
    alert(`Repeated login failures for ${userId} from ${ip}`);
    throttleOrLock(userId);   // coordinate with auth-hardening's lockout policy
  }
}
```

## Detection rules worth having (pick a few, keep them actionable)

- N failed logins per account or IP within a window → brute-force alert.
- Spike in access-denied (403) responses → enumeration / privilege probing.
- Admin action outside normal hours → review.
- Bulk export / large data read by a single actor → possible exfiltration.
- Login from a new country for an account → step-up verification.

Keep the alert set small and high-signal. Each alert should have a clear action;
an alert nobody responds to just trains people to ignore alerts.

## Integrity

- Write logs append-only where possible.
- Ship logs off the generating machine (central log store) so a compromised host
  can't rewrite its own trail.
- Use consistent UTC timestamps so events across services line up.
