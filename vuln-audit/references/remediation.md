# Remediation Patterns

Before/after fixes for each vulnerability class. Read the section matching the
finding. Examples are stack-neutral pseudocode; adapt to the actual framework.

## Contents
- Injection (SQL / NoSQL / command)
- XSS
- Broken access control / IDOR
- CSRF
- SSRF
- File upload

---

## Injection

**SQL — vulnerable:**
```js
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```
**Fixed (parameterized):**
```js
db.query('SELECT * FROM users WHERE email = $1', [email]);
// or with an ORM:
prisma.user.findUnique({ where: { email } });
```

**NoSQL — vulnerable (object injection):**
```js
db.users.findOne({ email: req.body.email, password: req.body.password });
// attacker sends { "email": {"$gt":""}, "password": {"$gt":""} }
```
**Fixed (validate and reject unexpected types):**
```js
const parsed = loginSchema.safeParse(req.body);
if (!parsed.success) return res.status(400).end();
const { email, password } = parsed.data; // schema requires bounded strings
```

**Command — vulnerable:**
```js
exec(`convert ${userFile} out.png`);   // shell string from input
```
**Fixed (no shell, argument array):**
```js
execFile('convert', [userFile, 'out.png']);
```

---

## XSS

**Vulnerable:**
```js
element.innerHTML = userComment;
```
**Fixed (textContent, no HTML parsing):**
```js
element.textContent = userComment;
```
**When rich HTML is genuinely needed — sanitize:**
```js
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userHtml);
```
Add defense in depth: `Content-Security-Policy: default-src 'self'`.

---

## Broken access control / IDOR

**Vulnerable — returns any order by id:**
```js
app.get('/orders/:id', auth, async (req, res) => {
  res.json(await orders.get(req.params.id));
});
```
**Fixed — ownership enforced:**
```js
app.get('/orders/:id', auth, async (req, res) => {
  const order = await orders.get(req.params.id);
  if (!order || order.userId !== req.userId) return res.status(404).end();
  res.json(order);
});
```
**Multi-tenant — always scope to tenant:**
```js
const order = await orders.findFirst({
  where: { id: req.params.id, tenantId: req.tenantId },
});
```
Returning 404 (not 403) for objects the caller can't access avoids confirming
they exist.

---

## CSRF

**Vulnerable — cookie-authenticated state change, no token:**
```js
app.post('/account/email', cookieAuth, updateEmail);
```
**Fixed — SameSite cookie + CSRF token:**
```js
res.cookie('sid', id, { httpOnly: true, secure: true, sameSite: 'strict' });
// verify a per-session CSRF token submitted in a header on state-changing requests
app.post('/account/email', cookieAuth, verifyCsrf, updateEmail);
```
Token-only APIs without cookies generally don't need CSRF tokens.

---

## SSRF

**Vulnerable — fetches a user URL directly:**
```js
const data = await fetch(req.body.url);
```
**Fixed — allowlist + resolve every address + no internal redirects:**
```js
const url = new URL(req.body.url);
if (!ALLOWED_HOSTS.has(url.hostname)) return res.status(400).end();
const addresses = await resolveAll(url.hostname);
if (!addresses.length || addresses.some(isPrivate)) return res.status(400).end();
const data = await fetch(url, { redirect: 'error' });
```

Enforce the same destination policy at the network egress layer and ensure the
HTTP client connects to an address that was actually validated; otherwise DNS
rebinding can separate validation from connection.

---

## File upload

**Vulnerable — trusts extension, stores in web root:**
```js
save(`/public/uploads/${file.originalname}`, file.buffer);
```
**Fixed — validate content, rename, store outside web root, cap size:**
```js
if (file.size > MAX) return res.status(413).end();
const kind = await fileTypeFromBuffer(file.buffer);   // inspect bytes, not name
if (!ALLOWED_MIME.has(kind?.mime)) return res.status(415).end();
const name = crypto.randomBytes(16).toString('hex') + '.' + kind.ext;
await objectStore.put(name, file.buffer);             // not a web-served path
```
