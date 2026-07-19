.PHONY: dev dev-down test test-auth test-patient lint build-auth clean

# ── Local Dev ────────────────────────────────────────────────────────
dev:
	docker compose up --build -d postgres redis auth-service
	@echo "✅  Auth service: http://localhost:8001"
	@echo "   PostgreSQL:    localhost:5432"
	@echo "   Redis:         localhost:6379"

dev-all:
	docker compose --profile sprint2 up --build -d

dev-down:
	docker compose down

dev-clean:
	docker compose down -v --remove-orphans

# ── Tests ────────────────────────────────────────────────────────────
test-auth:
	cd services/auth-service && go test ./... -v -race -count=1

test-patient:
	cd services/patient-data-service && go test ./... -v -race -count=1

test:
	@$(MAKE) test-auth
	@$(MAKE) test-patient

# ── Lint ─────────────────────────────────────────────────────────────
lint:
	cd services/auth-service && golangci-lint run ./...

# ── Build ────────────────────────────────────────────────────────────
build-auth:
	cd services/auth-service && docker build -t healthguard/auth-service:local .

# ── DB Migrations ────────────────────────────────────────────────────
migrate-up:
	psql "$(DATABASE_URL)" -f docs/schema/postgres.sql

migrate-down:
	@echo "Manual rollback — see docs/schema/postgres.sql for DROP statements"

# ── Terraform ────────────────────────────────────────────────────────
tf-plan-us:
	cd infra/terraform/us-east-1 && terraform init && terraform plan

tf-plan-eu:
	cd infra/terraform/eu-west-1 && terraform init && terraform plan

tf-apply-us: ## Requires human approval — do not run in CI
	cd infra/terraform/us-east-1 && terraform apply

# ── Utilities ────────────────────────────────────────────────────────
clean:
	find . -name "*.test" -delete
	find . -name "coverage.out" -delete
	cd services/auth-service && go clean ./...
