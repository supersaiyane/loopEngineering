<!-- LOAD-TYPE: CHECKLIST -->
---
id: secrets_management_cicd
version: 1.0.0
owners: [devops_engineer]
tags: [secrets, vault, aws-secrets-manager, environment-variables, rotation, cicd, security]
when_to_use: |
  Any secret: API keys, DB passwords, JWT signing keys, certificates.
  If it is not supposed to be public, it is a secret and needs managed storage.
  Never in source code, never in CI environment variables that are logged.
inputs:
  - secret_types, cloud_provider, rotation_requirements, team_access_needs
outputs:
  - "secrets_plan: storage location + injection method + rotation schedule + access policy"
---

# Secrets Management in CI/CD

> A secret in source code is not a secret.
> A secret in a CI log is not a secret.
> A secret that never rotates is a ticking clock.

## Secret storage options

| Tool | Best for | Rotation | Audit |
|---|---|---|---|
| AWS Secrets Manager | AWS-native workloads | Auto-rotation built in | CloudTrail |
| HashiCorp Vault | Multi-cloud, on-prem | Dynamic secrets | Built-in audit log |
| GitHub Actions Secrets | CI/CD only | Manual | GitHub audit log |
| GCP Secret Manager | GCP-native | Versioned | Cloud Audit Logs |
| Kubernetes Secrets | K8s workloads (with encryption at rest) | Manual | K8s audit log |

## AWS Secrets Manager pattern

```python
# Runtime: fetch secret at startup, not hardcoded
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# At app startup
secrets = get_secret("prod/api-service/db")
DB_URL = f"postgresql://{secrets["username"]}:{secrets["password"]}@{secrets["host"]}/mydb"
```

```python
# Auto-rotation Lambda (AWS handles this for RDS)
def rotate_secret(event, context):
    """Called by Secrets Manager during rotation."""
    step = event["Step"]
    if step == "createSecret":
        # Generate new credentials
        new_password = generate_secure_password()
        client.put_secret_value(
            SecretId=event["SecretId"],
            ClientRequestToken=event["ClientRequestToken"],
            SecretString=json.dumps({**current_secret, "password": new_password}),
            VersionStages=["AWSPENDING"],
        )
    elif step == "setSecret":
        # Apply new credentials to DB
        apply_new_password_to_db(new_password)
    elif step == "finishSecret":
        # Mark as current
        client.update_secret_version_stage(...)
```

## HashiCorp Vault dynamic secrets

```bash
# Dynamic DB credentials: Vault generates unique creds per app instance
# No shared password -- each service gets its own expiring credentials

vault secrets enable database
vault write database/config/mydb     plugin_name=postgresql-database-plugin     connection_url="postgresql://{{username}}:{{password}}@db:5432/mydb"     allowed_roles="api-service"

vault write database/roles/api-service     db_name=mydb     creation_statements="CREATE ROLE ... WITH LOGIN PASSWORD '{{password}}'"     default_ttl="1h"     max_ttl="24h"

# App fetches creds: unique per instance, auto-expires in 1h
vault read database/creds/api-service
# Key         Value
# username    v-api-AbCdEf
# password    A1b2C3d4-...   (generated, expires in 1h)
```

## CI/CD: inject secrets safely

```yaml
# GitHub Actions: secrets never appear in logs (masked)
jobs:
  deploy:
    steps:
      - name: Deploy
        env:
          DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
          API_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
        run: ./deploy.sh
        # Secrets are masked in logs: "***" appears instead of value

# Never: echo $DB_PASSWORD  # this logs the secret even though it appears masked in some CI systems
# Never: export in shell script that gets logged
```

```yaml
# Kubernetes: mount secrets as files (not environment variables)
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: api
      volumeMounts:
        - name: db-secret
          mountPath: /secrets/db
          readOnly: true
      # App reads /secrets/db/password -- not from env var
  volumes:
    - name: db-secret
      secret:
        secretName: api-service-db-secret
```

## Secret scanning in CI

```yaml
# Pre-commit hook: detect secrets before they reach git
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

# CI check: scan entire repo history
- name: Gitleaks scan
  run: gitleaks detect --source . --baseline-path .gitleaks-baseline.json
```

## Anti-patterns

- **Secrets in source code**: git history is forever. Rotate immediately if this happens.
- **Secrets in CI environment variables that are printed**: `echo $API_KEY` in logs.
- **Never rotating secrets**: assume breach. Rotate quarterly at minimum.
- **Shared secrets across environments**: prod key accessible in dev = blast radius is all envs.
- **Kubernetes Secrets without encryption at rest**: base64 is not encryption.

## Validation

- [ ] No secrets in source code (gitleaks scan passes).
- [ ] All production secrets in managed store (Vault, AWS SM, etc.).
- [ ] Rotation schedule defined and tested for each secret.
- [ ] Least-privilege: each service has access only to its own secrets.
- [ ] Secret access audit log reviewed quarterly.
