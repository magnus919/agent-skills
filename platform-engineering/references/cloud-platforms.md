# Cloud Platforms — Reference

> **Last Updated:** 2026-08-03
> Patterns and decision guidance for cloud platform architecture. Operational configuration belongs to the tool skills (`terraform`, `kubernetes`, `docker-compose`, `traefik`); this file carries judgment frameworks.

## Provider Selection — Decision Guidance

### AWS

- **Core services:** VPC (subnets, route tables, NAT, security groups, NACLs, VPC peering, Transit Gateway), EC2 (instances, AMIs, auto-scaling, launch templates, spot), EKS (managed K8s, node groups, Fargate, IRSA), S3 (buckets, versioning, lifecycle, replication, presigned URLs), IAM (users, roles, policies, instance profiles, OIDC), Route53 (DNS, alias records, health checks, routing policies)
- **Common patterns:** Shared VPC (central networking team), multi-account (Control Tower, Organization, SCPs), IRSA for EKS pod IAM, S3 backend for Terraform state (bucket + DynamoDB lock), CodeBuild/CodePipeline for CI, CloudFront for CDN
- **When AWS fits:** Broadest service catalog, deepest managed-K8s and IAM maturity, most mature IaC ecosystem and third-party tooling. Strong default when the team already has AWS skills or needs services no other provider matches.

### GCP

- **Core services:** VPC (subnets, firewall rules, Cloud NAT, VPC peering, Shared VPC), GKE (K8s, node auto-repair/auto-upgrade, Workload Identity for pod IAM), Cloud Storage (buckets, nearline/archive, object lifecycle), IAM (roles, custom roles, service accounts, Workload Identity Federation), Cloud DNS (managed zones, DNS forwarding, policy-based routing)
- **Common patterns:** Shared VPC (host project + service projects), workload identity federation (no static keys), Artifact Registry, Cloud Build CI, Terraform state via Cloud Storage
- **When GCP fits:** Kubernetes-first workloads (GKE is the closest managed-K8s experience), data/ML platform strengths, most aggressive committed-use discounts, clean identity-federation story for keyless workloads.

### Azure

- **Core services:** VNet (subnets, NSGs, Azure Bastion, VPN Gateway, VNet peering), AKS (K8s, node pools, managed identity, Azure AD integration), Blob Storage (containers, tiers, lifecycle, Azure Files), RBAC (roles, custom roles, managed identities, service principals), DNS (public/private zones, alias records, Azure DNS Private Resolver)
- **Common patterns:** Hub-and-spoke networking (central firewall), managed identity for pod IAM (AKS with workload identity), Terraform state via Azure Storage, Azure DevOps pipelines
- **When Azure fits:** Windows/.NET/Active Directory shops, enterprise compliance and procurement (existing Microsoft agreements), hybrid on-prem connectivity, regulated industries where Azure's compliance footprint is a sales advantage.

## Multi-Cloud and Abstraction

- **Abstraction layers:** Terraform/OpenTofu providers — write once, target any cloud (with provider-specific variance). Pulumi similarly abstracts. Crossplane for K8s-native cloud resource provisioning
- **Governance cost:** State isolation per cloud, IAM duplication per provider, network egress charges (Free Tier per cloud but real cost at scale), skills distribution across cloud teams
- **When multi-cloud is worth it:** Regulatory (data residency), avoiding single-vendor lock-in for critical few services (object storage, K8s), acquisition integration. It is NOT a cost-savings strategy.
- **When multi-cloud is a trap:** Teams assume abstraction layers erase provider differences; they do not. Each provider's IAM model, quota semantics, and operational behavior leak through. A second provider doubles the platform surface for zero resilience unless workloads are actually replicated (active-active or active-passive with real failover testing).
- **Decision rule:** Start single-cloud. Add a second provider only for a named, measurable requirement (residency, availability, acquisition). If the goal is resilience, prove failover works before committing to the second provider.

## Cost Governance Patterns

- **Budget alerts** (each cloud): per-account/project budget with alert thresholds at 50/80/100%, billing exports to a data warehouse for cost analytics
- **Tagging policies:** `CostCenter`, `Environment`, `Owner`, `Service` — enforced at provisioning time (guardrails/Terraform validators), not retroactively
- **Right-sizing:** instance/container resource analysis against utilization, right-size before scaling out
- **Committed use:** reserved instances / committed use discounts / savings plans for steady-state baseline; spot/preemptible for batch and stateless workloads
- **Storage tier policies:** lifecycle rules moving cold data to archive tiers; know the retrieval cost before designing hot paths
- **Egress awareness:** egress charges dominate surprise bills; keep data transfer within a region/zone where possible, and route cross-provider traffic deliberately
- **FinOps cadence:** monthly cost review with owners, anomaly detection on the billing feed, unit-economics per service (see `capacity-and-cost-engineering` for the methodology)

## Security and Identity Patterns

- **Workload identity over static keys:** OIDC federation (IRSA, Workload Identity Federation, managed identity) so pods and CI never hold long-lived cloud keys
- **Multi-account/project structure as the security boundary:** control plane (org/root) separate from workload accounts, SCPs as policy guardrails, audit account for centralized logs
- **Shared responsibility model:** the provider secures the fabric; the platform team owns IAM, network boundaries, data encryption at rest/in transit, and image/artifact supply chain
- **Audit logging:** enable cloud trail/audit logs centrally with retention and alerting on privileged-role usage

## Sources and Dated References

- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/ (accessed 2026-08-03)
- AWS Organizations multi-account best practices: https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html (accessed 2026-08-03)
- GCP resource hierarchy and IAM: https://cloud.google.com/docs/overview (accessed 2026-08-03)
- Azure cloud adoption framework / landing zones: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ (accessed 2026-08-03)
- FinOps framework and cost optimization: https://www.finops.org/framework/ (accessed 2026-08-03)
