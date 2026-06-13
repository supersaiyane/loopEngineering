<!-- LOAD-TYPE: CHECKLIST -->
---
id: saml_security
version: 1.0.0
owners: [security_engineer, architect]
tags: [security, auth, saml, sso, identity]
when_to_use: >
  Any story implementing SAML 2.0 SP-initiated or IdP-initiated SSO flows,
  integrating with Okta/Azure AD/PingFederate, or building a SAML metadata
  endpoint. Mandatory for be/auth stories where SAML is the auth mechanism.
---

# SAML 2.0 Security Checklist

FULL-LOAD REQUIRED — compress-to-5-lines destroys security coverage.

---

## A1 — XML External Entity (XXE) Prevention

SAML assertions are XML. Default XML parsers resolve external entities — attackers can exfiltrate files or SSRF via crafted SAML responses.

**Checklist:**
- [ ] XML parser has external entity resolution DISABLED (`resolve_entities=False` in lxml, `FEATURE_EXTERNAL_GENERAL_ENTITIES=false` in Java SAX)
- [ ] DTD processing disabled (`load_dtd=False`)
- [ ] Test: send SAML response with `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>` — parser must reject or ignore
- [ ] Log test result: `[XXE: BLOCKED | parser=<name> | setting=<config key>]`

---

## A2 — Assertion Signature Validation

SAML responses and assertions must be cryptographically signed. Accepting unsigned or self-signed assertions = auth bypass.

**Checklist:**
- [ ] Signature validated on BOTH the `<Response>` element AND the `<Assertion>` element (not just one)
- [ ] IdP certificate pinned from metadata URL (not accepted from the SAML response itself)
- [ ] Certificate expiry checked at validation time
- [ ] Weak signature algorithms rejected: SHA-1 blocked. Accept only SHA-256+.
- [ ] Test: send response with missing signature → must return 401, not 200
- [ ] Test: send response with tampered signature → must reject
- [ ] Log: `[SAML-SIG: Response=✅ | Assertion=✅ | cert=pinned | algo=SHA256]`

---

## A3 — Replay Attack Prevention (InResponseTo)

SAML responses include an `InResponseTo` attribute tying the assertion to a specific SP-generated `AuthnRequest`. Without validation, stolen assertions can be replayed.

**Checklist:**
- [ ] SP generates a unique `ID` on every `AuthnRequest` (UUID or cryptographic random)
- [ ] `InResponseTo` in SAML response matched against stored `AuthnRequest ID`
- [ ] `AuthnRequest ID` is single-use — consumed on first use, never reusable
- [ ] `AuthnRequest ID` expires after configurable TTL (recommend ≤ 5 minutes)
- [ ] Test: replay same SAML response twice → second use rejected
- [ ] Test: send response with `InResponseTo` pointing to unknown request → rejected

---

## A4 — Assertion Conditions Validation

SAML assertions contain `<Conditions>` with `NotBefore` and `NotOnOrAfter` timestamps and `<AudienceRestriction>`. Ignoring these enables assertion reuse across time and services.

**Checklist:**
- [ ] `NotBefore` checked — reject assertions not yet valid
- [ ] `NotOnOrAfter` checked — reject expired assertions
- [ ] Clock skew tolerance: max ±2 minutes (not unlimited)
- [ ] `<AudienceRestriction>` contains the SP's Entity ID — reject if wrong audience
- [ ] Test: send assertion with `NotOnOrAfter` in the past → rejected
- [ ] Test: send assertion with wrong `Audience` → rejected

---

## A5 — ACS URL Binding Validation

Assertion Consumer Service (ACS) URL in the `AuthnRequest` must match a pre-registered URL. If the IdP reflects back whatever ACS URL the SP sends, an attacker can redirect assertions to an attacker-controlled endpoint.

**Checklist:**
- [ ] ACS URL pre-registered in IdP metadata (not dynamically accepted from SP request)
- [ ] SP validates the ACS URL in its own metadata before using it
- [ ] IdP does not accept arbitrary ACS URLs from incoming `AuthnRequest`
- [ ] Log: `[ACS: validated | url=<registered-url>]`

---

## A6 — IdP Metadata Management

**Checklist:**
- [ ] IdP metadata fetched from HTTPS metadata URL (not manually uploaded and never updated)
- [ ] Metadata refresh scheduled (recommend: every 24h or on cert rotation events)
- [ ] Certificate rollover handled: SP accepts signing cert from metadata `<ds:KeyDescriptor use="signing">`, not hardcoded cert
- [ ] Test: rotate IdP signing cert → SP continues to work without manual intervention

---

## A7 — IdP-Initiated Flow Risks

IdP-initiated flows (no prior `AuthnRequest`) skip InResponseTo validation entirely. This is a weaker security posture.

**Checklist:**
- [ ] IdP-initiated flow explicitly disabled IF not required by product spec
- [ ] If enabled: additional validation applied — assertion must arrive within tight time window (≤ 2 min from `IssueInstant`)
- [ ] Log: `[SAML-FLOW: SP-initiated ✅ | IdP-initiated: disabled/enabled+TTL]`

---

## A8 — Session Management After SAML Login

**Checklist:**
- [ ] New session ID generated after SAML login (session fixation prevention)
- [ ] SAML `SessionIndex` stored for Single Logout (SLO) support
- [ ] Session bound to user-agent + IP (configurable — some enterprises use VPNs)
- [ ] Session expiry respects SAML `SessionNotOnOrAfter` if present

---

## VERIFIER COMMANDS

```bash
# XXE test (Python/lxml)
python -c "
from lxml import etree
p = etree.XMLParser(resolve_entities=False, load_dtd=False)
try:
    etree.fromstring(b'<!DOCTYPE x [<!ENTITY e SYSTEM \"file:///etc/passwd\">]><x>&e;</x>', p)
    print('FAIL: XXE not blocked')
except: print('PASS: XXE blocked')
"

# Replay test — run twice with same assertion, expect 2nd to fail
npm run test:saml:replay

# Signature validation
npm run test:saml:signature

# Conditions expiry
npm run test:saml:conditions
```

---

## CRITERIA TEMPLATES (for loop spec)

```
SAML-XXE: XML parser rejects external entity injection (score 1-10)
SAML-SIG: Response + Assertion both signature-validated, SHA-256 only (score 1-10)
SAML-REPLAY: InResponseTo validated, ID single-use with 5min TTL (score 1-10)
SAML-CONDITIONS: NotBefore/NotOnOrAfter + AudienceRestriction enforced (score 1-10)
SAML-ACS: ACS URL pre-registered, not dynamically accepted (score 1-10)
```

Use max 2 SAML criteria per story (STRIDE-BRIDGE rule). Pick the two highest-risk for the story's scope.
