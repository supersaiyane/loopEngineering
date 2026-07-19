# ADR-004: Multi-Region AWS Deployment (us-east-1 + eu-west-1)

**Date:** 2026-07-17  
**Status:** Accepted  

## Context

GDPR Article 46 prohibits transfer of EU personal data outside the EEA without adequate safeguards. US hospitals are subject to HIPAA. Both regions must be independently compliant.

## Decision

Deploy independent stacks in us-east-1 (US) and eu-west-1 (EU). **No VPC peering between regions.**

## Architecture

```
users.region / patients.region / tenants.region
          │
          ├── 'us-east-1' → us-east-1 EKS + RDS + ClickHouse
          └── 'eu-west-1' → eu-west-1 EKS + RDS + ClickHouse
                                 ↑ EU data NEVER leaves this cluster
```

**Route 53:** Geolocation routing — EU countries → eu-west-1, all others → us-east-1.

## Hard Constraints (enforced by Terraform)

- S3 buckets: `aws_s3_bucket_replication_configuration` BLOCKED in eu-west-1 (no cross-region copy)
- RDS: no cross-region read replicas for eu-west-1
- ClickHouse: eu-west-1 cluster isolated, no replication to us-east-1
- VPC: no peering between regions (Terraform `aws_vpc_peering_connection` absent from eu-west-1)

## Consequences

✅ GDPR Article 46 compliance  
✅ HIPAA data residency  
✅ Independent fault domains (us outage doesn't affect EU)  
⚠️ Operational complexity: 2 Terraform workspaces, 2 EKS clusters  
⚠️ No shared analytics across regions (by design — GDPR)  
⚠️ Schema migrations must be applied to both regions independently
