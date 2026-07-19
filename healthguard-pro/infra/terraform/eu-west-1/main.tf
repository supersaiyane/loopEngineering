terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "healthguard-tfstate-eu-west-1"
    key    = "eu-west-1/terraform.tfstate"
    region = "eu-west-1"  # State bucket ALSO in eu-west-1 (data residency)
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = {
      Product     = "HealthGuard Pro"
      Environment = var.environment
      Region      = "eu-west-1"
      ManagedBy   = "Terraform"
      Compliance  = "GDPR"   # EU stack tagged separately from HIPAA
    }
  }
}

variable "environment" {
  type    = string
  default = "production"
}

# GDPR HARD CONSTRAINT:
# This module intentionally has NO cross-region replication.
# No aws_s3_bucket_replication_configuration.
# No aws_db_instance.replicate_source_db pointing outside eu-west-1.
# No aws_vpc_peering_connection to us-east-1.
# These are architectural guardrails — do not add them.

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "healthguard-eu-west-1"
  cidr = "10.1.0.0/16"  # Different CIDR from us-east-1 (no peering, but good hygiene)

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  public_subnets  = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

module "eks" {
  source = "../modules/eks"

  cluster_name    = "healthguard-eu-west-1-${var.environment}"
  region          = "eu-west-1"
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  node_count      = var.environment == "production" ? 4 : 2
  node_type       = var.environment == "production" ? "m6i.2xlarge" : "t3.xlarge"
}

resource "aws_db_instance" "postgres" {
  identifier        = "healthguard-eu-west-1-${var.environment}"
  engine            = "postgres"
  engine_version    = "16.2"
  instance_class    = var.environment == "production" ? "db.r7g.xlarge" : "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true
  multi_az          = var.environment == "production"

  db_name  = "healthguard"
  username = "healthguard"
  manage_master_user_password = true

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"

  # GDPR: EU data must stay in eu-west-1
  # backup_target = "region"  (default — no cross-region backup)

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

resource "aws_db_subnet_group" "main" {
  name       = "healthguard-eu-west-1"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "rds" {
  name   = "healthguard-rds-eu-west-1"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

output "eks_cluster_endpoint" { value = module.eks.cluster_endpoint }
output "vpc_id"               { value = module.vpc.vpc_id }
output "rds_endpoint"         { value = aws_db_instance.postgres.endpoint }
