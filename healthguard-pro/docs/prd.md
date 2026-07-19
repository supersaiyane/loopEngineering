# Product Requirements Document — HealthGuard Pro v1

**Author:** CTO  
**Date:** 2026-07-17  
**Status:** Approved — Sprint 1 baseline  
**Template:** prd_template.md (Fix 32A)  

---

## 1. Problem Statement

Hospital networks face three compounding crises:

1. **Sepsis is killing people who shouldn't die.** Sepsis kills 270,000 Americans annually. 80% of sepsis deaths are preventable with early detection. Existing EHR systems surface vital sign data but provide no real-time risk scoring — nurses must mentally pattern-match across dozens of patients simultaneously.

2. **Auth is a phishing liability.** Clinicians use weak, shared passwords across workstations. HIPAA breach reports show 58% of healthcare breaches involve compromised credentials. There is no passwordless option in any mainstream hospital software.

3. **IT provisioning is manual and dangerous.** When a nurse leaves, IT must manually deactivate their account across 6–12 systems. On average, ex-employee accounts remain active for 11 days after termination — creating HIPAA liability.

---

## 2. Goals

| # | Goal | Metric |
|---|------|--------|
| G1 | Real-time sepsis risk score per patient | P99 inference latency < 500ms |
| G2 | Zero cross-tenant data leakage | 0 incidents in production |
| G3 | Eliminate credential phishing vector | 100% of clinicians on WebAuthn by GA |
| G4 | Automated provisioning/deprovisioning | < 60 seconds from HR termination to access revoked |
| G5 | HIPAA + GDPR compliance on Day 1 | BAA signed before first data ingested |

---

## 3. Non-Goals (explicit — prevents scope creep, Fix 32A)

- **NOT an EHR replacement.** HealthGuard Pro reads from existing EHRs via HL7 FHIR. It does not replace Epic, Cerner, or Meditech.
- **NOT building our own HL7 FHIR parser.** Using HAPI FHIR (Java, Apache 2.0, Rung 2).
- **NOT supporting on-premise deployment in v1.** Cloud-only. On-prem is a v2 decision.
- **NOT building our own AI model from scratch.** Using transfer learning on published sepsis datasets (MIMIC-IV, eICU).
- **NOT billing per patient.** Billing model: per-seat (clinician accounts) + per-API-call (FHIR reads). Not per-patient.
- **NOT supporting SSO via SAML 2.0 in Sprint 1.** Deferred to Sprint 2 (IAM budget constraint — see ADR-003).

---

## 4. User Personas

| Persona | Role | Primary Pain | Key Jobs-to-be-Done |
|---------|------|-------------|-------------------|
| **ICU Nurse (Maya)** | Bedside clinician | Monitoring 12 patients at once, can't catch early sepsis | See risk score per patient, get alerted before it's critical |
| **Hospital IT Admin (Raj)** | IT provisioning | Manual SCIM setup, ex-employee access risk | Plug Okta into SCIM, set it and forget it |
| **Hospital CFO (Dr. Chen)** | Buyer / approver | HIPAA liability, cost of sepsis cases | ROI: sepsis cost avoided vs. subscription cost |
| **ICU Physician (Dr. Patel)** | Clinical oversight | Alarm fatigue from too many false positives | High-precision alerts only (< 12% false positive rate) |

---

## 5. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sepsis alert sensitivity | ≥ 85% | Model evaluation on holdout set |
| False positive rate | < 12% | Model evaluation on holdout set |
| Inference latency P99 | < 500ms | Load test: 500 concurrent requests |
| Time to deprovision | < 60 seconds | E2E test: SCIM DELETE → access denied |
| Cross-tenant leak incidents | 0 | GATE S2 cross-tenant denial tests |
| WebAuthn registration success rate | > 98% | Product analytics |

---

## 6. Constraints

### HARD (non-negotiable — from TRD)
- EU patient data MUST NOT leave eu-west-1 (GDPR Article 46)
- ALL queries MUST include `WHERE tenant_id = $current_tenant_id`
- HIPAA BAA signed before first hospital data is ingested
- WebAuthn `userVerification = required` (not `preferred`)

### SOFT (target, negotiable)
- Sepsis inference P99 < 500ms (can relax to 1s if model complexity requires)
- Mobile app: iOS first, Android follows (can be same sprint if MOBILE_ENGINEER capacity allows)
- ClickHouse cluster: start with 3 nodes, auto-scale

---

## 7. Label Map (story → label routing for SM-PLAN)

```
Epic HEALTHGUARD-001 — Auth Platform
  AUTH-001: WebAuthn registration          [be/auth, security-critical]
  AUTH-002: SAML 2.0 SSO                  [be/auth]              ← DEFERRED Sprint 2
  AUTH-003: SCIM 2.0 provisioning         [be/api]
  AUTH-004: RBAC role enforcement          [be/auth, security-critical]

Epic HEALTHGUARD-002 — Patient Data
  PAT-001: Patient CRUD + tenant isolation [be/api, e2e-required]
  PAT-002: Vitals ingestion pipeline       [be/data]
  PAT-003: HIPAA audit log                 [be/data]

Epic HEALTHGUARD-003 — Sepsis AI
  ML-001: Feature engineering pipeline    [data/ml]
  ML-002: Model training + evaluation     [data/ml]
  ML-003: Real-time inference API         [data/ml, real-time/*]
  ML-004: Score ingestion to ClickHouse   [data/pipeline]

Epic HEALTHGUARD-004 — Real-time Alerts
  RT-001: WebSocket gateway               [real-time/*]
  RT-002: Alert rule engine               [be/api]
  RT-003: Push notifications (mobile)     [mobile/ios, mobile/android]

Epic HEALTHGUARD-005 — Mobile App
  MOB-001: Patient iOS scaffold           [mobile/ios]
  MOB-002: Patient Android scaffold       [mobile/android]
  MOB-003: Clinician mobile dashboard     [mobile/ios, mobile/android]

Epic HEALTHGUARD-006 — Infrastructure
  INFRA-001: EKS cluster + VPC            [infra/deploy]
  INFRA-002: CI/CD pipeline               [infra/deploy]
  INFRA-003: ClickHouse cluster           [infra/deploy]
  INFRA-004: Multi-region RDS             [infra/deploy]
```

---

## 8. Open Questions (OQ log)

| # | Question | Owner | Resolution |
|---|----------|-------|------------|
| OQ-01 | Which hospital signs as design partner for beta? | CEO | Pending — blocking HIPAA BAA |
| OQ-02 | MIMIC-IV or eICU for initial model training? | DATA_SCIENTIST | MIMIC-IV (larger, ICU-focused) |
| OQ-03 | SAML IdP priority: Okta or Azure AD first? | Product | Okta first (Sprint 2 target) |

---

*PRD approved by CTO · 2026-07-17 · GATE 2 prerequisite satisfied*
