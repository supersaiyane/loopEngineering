# INFRA-001 — EKS Cluster + VPC (Terraform)

**Epic:** HEALTHGUARD-006 — Infrastructure  
**Sprint:** 1  
**Points:** 5 (L)  
**Labels:** `infra/deploy`  
**Primary Agent:** DEVOPS_ENGINEER  
**Co-Agent:** SRE_ENGINEER  
**Status:** ✅ DONE  

---

## User Story

> **As a** DEVOPS_ENGINEER standing up HealthGuard Pro's cloud infrastructure,  
> **I want to** provision an EKS cluster and VPC in us-east-1 (HIPAA) and eu-west-1 (GDPR) via Terraform,  
> **So that** all services have a HIPAA/GDPR-compliant runtime environment from day one.

---

## Acceptance Criteria

- [ ] `infra/terraform/us-east-1/` provisions: VPC (10.0.0.0/16), EKS 1.30, RDS PostgreSQL 16 Multi-AZ
- [ ] `infra/terraform/eu-west-1/` provisions: VPC (10.1.0.0/16), EKS 1.30, RDS PostgreSQL 16 Multi-AZ
- [ ] EKS endpoint `public_access = false` (no public API server)
- [ ] KMS CMK encrypts EKS secrets at rest
- [ ] RDS: Multi-AZ, encrypted storage, CloudWatch + Performance Insights enabled
- [ ] **HARD CONSTRAINT: NO VPC peering between us-east-1 and eu-west-1** (GDPR data residency)
- [ ] **HARD CONSTRAINT: NO cross-region S3 replication** (GDPR data residency)
- [ ] Terraform state stored in separate S3 buckets per region (not shared)
- [ ] `terraform validate` passes for both regions
- [ ] All resources tagged: `Project=HealthGuardPro`, `Compliance=HIPAA` or `Compliance=GDPR`, `ManagedBy=Terraform`

---

## Compliance Architecture

```
us-east-1 (HIPAA)          eu-west-1 (GDPR)
───────────────────         ────────────────────
VPC 10.0.0.0/16             VPC 10.1.0.0/16
EKS 1.30 (private)          EKS 1.30 (private)
RDS Multi-AZ (enc)          RDS Multi-AZ (enc)
S3 state bucket             S3 state bucket (eu-west-1)
                                                     
     ↑                           ↑
     NO VPC PEERING              NO CROSS-REGION REPLICATION
     (hard constraint — GDPR Article 46)
```

---

## Technical Notes

**Terraform modules:**
- `infra/terraform/modules/eks/main.tf` — reusable EKS module
- `infra/terraform/us-east-1/main.tf` — HIPAA deployment
- `infra/terraform/eu-west-1/main.tf` — GDPR deployment

**EKS node group:** `t3.large`, min 2 / desired 3 / max 10 (Sprint 1 — scale in Sprint 2).  
**RDS instance:** `db.t3.medium` for Sprint 1, `db.r6g.large` from Sprint 2.  
**Backend:** Remote state in S3 with DynamoDB locking. Each region has its own state bucket — never shared.  

**ADR reference:** ADR-004 (multi-region, no VPC peering).

---

## GATE S2 Checklist

```
✅  terraform validate (us-east-1)          — PASS
✅  terraform validate (eu-west-1)          — PASS
✅  tfsec scan                              — 0 HIGH/CRITICAL findings
✅  No secrets committed                    — no AWS keys in any .tf file ✅
✅  GDPR hard constraint verified           — NO replication_configuration, NO VPC peering ✅
✅  HIPAA hard constraint verified          — endpoint_public_access = false, KMS enabled ✅
✅  Resource tagging review                 — Compliance tag on all resources ✅
```

**GATE S2: PASS → INFRA-001 MERGED**

---

## Linked Files

- `infra/terraform/modules/eks/main.tf`
- `infra/terraform/us-east-1/main.tf`
- `infra/terraform/eu-west-1/main.tf`
- `docs/adr/004-multi-region-no-peering.md`
- `docs/trd.md#trust-boundary-map`
