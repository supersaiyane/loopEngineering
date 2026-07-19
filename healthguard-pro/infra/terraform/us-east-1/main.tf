terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "healthguard-tfstate-us-east-1"
    key    = "us-east-1/terraform.tfstate"
    region = "us-east-1"
    # encrypt = true
    # dynamodb_table = "healthguard-tfstate-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags { tags = local.common_tags }
}

locals {
  env  = var.environment
  region = "us-east-1"
  common_tags = {
    Product     = "HealthGuard Pro"
    Environment = local.env
    Region      = local.region
    ManagedBy   = "Terraform"
    Compliance  = "HIPAA"
  }
}

variable "environment" {
  type    = string
  default = "production"
}

# ── VPC ─────────────────────────────────────────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "healthguard-us-east-1"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = local.env != "production"
  enable_vpn_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # HIPAA: no cross-region replication from this VPC
  tags = local.common_tags
}

# ── EKS ─────────────────────────────────────────────────────────────────────
module "eks" {
  source = "../modules/eks"

  cluster_name    = "healthguard-us-east-1-${local.env}"
  region          = local.region
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  node_count      = local.env == "production" ? 6 : 3
  node_type       = local.env == "production" ? "m6i.2xlarge" : "t3.xlarge"
  tags            = local.common_tags
}

# ── RDS PostgreSQL Multi-AZ ──────────────────────────────────────────────────
resource "aws_db_instance" "postgres" {
  identifier        = "healthguard-us-east-1-${local.env}"
  engine            = "postgres"
  engine_version    = "16.2"
  instance_class    = local.env == "production" ? "db.r7g.xlarge" : "db.t3.medium"
  allocated_storage = 100
  storage_type      = "gp3"
  storage_encrypted = true
  multi_az          = local.env == "production"

  db_name  = "healthguard"
  username = "healthguard"
  # password managed by AWS Secrets Manager
  manage_master_user_password = true

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period  = 7
  delete_automated_backups = false
  deletion_protection      = local.env == "production"
  skip_final_snapshot      = local.env != "production"

  # HIPAA: enable enhanced monitoring + performance insights
  monitoring_interval           = 60
  monitoring_role_arn           = aws_iam_role.rds_monitoring.arn
  performance_insights_enabled  = true
  performance_insights_retention_period = 7

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = local.common_tags
}

resource "aws_db_subnet_group" "main" {
  name       = "healthguard-us-east-1"
  subnet_ids = module.vpc.private_subnets
  tags       = local.common_tags
}

resource "aws_security_group" "rds" {
  name   = "healthguard-rds-us-east-1"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]  # VPC-internal only
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = local.common_tags
}

resource "aws_iam_role" "rds_monitoring" {
  name = "healthguard-rds-monitoring-us-east-1"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "monitoring.rds.amazonaws.com" }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ── Outputs ──────────────────────────────────────────────────────────────────
output "eks_cluster_endpoint" { value = module.eks.cluster_endpoint }
output "vpc_id"               { value = module.vpc.vpc_id }
output "rds_endpoint"         { value = aws_db_instance.postgres.endpoint }
