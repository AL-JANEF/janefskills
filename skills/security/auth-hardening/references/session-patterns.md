# Session Patterns

Concrete implementations for the three session models. Read the section that
matches the user's stack. All examples are Node.js / Express-style pseudocode;
adapt naming to Next.js route handlers or the actual framework in use.

## Contents
- Stateful sessions (server-stored)
- Stateless JWT with revocation
- Refresh-token rotation
- Password hashing reference

---

## Stateful sessions (server-stored)

The session lives on the server; the client holds only an opaque ID. Logout is a
single delete and is genuinely effective.

```js
// Login: create a server-side session, return an opaque id in an httpOnly cookie
const sessionId = crypto.randomBytes(32).toString('hex');
await sessions.set(sessionId, {
  userId: user.id,
  createdAt: Date.now(),
  expiresAt: Date.now() + 1000 * 60 * 60 * 24, // 24h
});
res.cookie('sid', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  maxAge: 1000 * 60 * 60 * 24,
});

// Auth middleware: look up the session each request
const record = await sessions.get(req.cookies.sid);
if (!record || record.expiresAt < Date.now()) return res.status(401).end();
req.userId = record.userId;

// Logout: delete the record — the session is now dead everywhere
await sessions.delete(req.cookies.sid);
res.clearCookie('sid');
```

Store sessions in Redis or a database, not in process memory (memory doesn't
survive restarts or scale across instances).

---

## Stateless JWT with revocation

A JWT can't be un-issued, so add a revocation mechanism. The lightest is a
per-user token version bumped on logout / password change.

```js
// User row carries a tokenVersion integer, starting at 0.

// Login: embed the current version in the token
const token = jwt.sign(
  { sub: user.id, ver: user.tokenVersion },
  SECRET,
  { expiresIn: '15m', issuer: 'your-app', audience: 'your-app' }
);

// Verify: pin the algorithm and check the version still matches
const payload = jwt.verify(token, SECRET, {
  algorithms: ['HS256'],          // never allow 'none' or a caller-chosen alg
  issuer: 'your-app',
  audience: 'your-app',
});
const user = await users.get(payload.sub);
if (!user || user.tokenVersion !== payload.ver) return res.status(401).end();

// Logout / password change: bump the version — every old token now fails
await users.update(user.id, { tokenVersion: user.tokenVersion + 1 });
```

Alternative: a denylist of revoked token IDs (`jti`) held in Redis with a TTL
equal to the token's remaining lifetime. Heavier but revokes individual tokens
rather than all of a user's tokens at once.

---

## Refresh-token rotation

Short access token + long, revocable refresh token. Rotate the refresh token on
every use so a stolen one is single-use and detectable.

```js
// On login: issue a short access token + a refresh token stored server-side
const refreshId = crypto.randomBytes(32).toString('hex');
await refreshTokens.set(refreshId, { userId: user.id, used: false,
  expiresAt: Date.now() + 1000 * 60 * 60 * 24 * 30 });

// On refresh:
const rec = await refreshTokens.get(refreshId);
if (!rec || rec.expiresAt < Date.now()) return res.status(401).end();
if (rec.used) {
  // Reuse of an already-rotated token = likely theft.
  // Revoke the whole family for this user and force re-login.
  await refreshTokens.revokeAllForUser(rec.userId);
  return res.status(401).end();
}
await refreshTokens.markUsed(refreshId);           // rotate: old one is now spent
const newRefreshId = crypto.randomBytes(32).toString('hex');
await refreshTokens.set(newRefreshId, { userId: rec.userId, used: false,
  expiresAt: Date.now() + 1000 * 60 * 60 * 24 * 30 });
// issue new access token + return newRefreshId
```

The reuse-detection branch is the point of rotation: if a spent refresh token
appears again, someone has a copy, so you burn the whole family.

---

## Password hashing reference

```js
import argon2 from 'argon2';

// Hash on signup / password change
const hash = await argon2.hash(password, { type: argon2.argon2id });

// Verify on login
const ok = await argon2.verify(hash, submittedPassword);
```

bcrypt is an acceptable alternative (cost factor >= 12). Do not use fast hashes
(MD5, SHA-*) or HMAC for passwords — those belong to token signing, not password
storage. Migrate legacy fast-hashed passwords by re-hashing on next successful
login.
