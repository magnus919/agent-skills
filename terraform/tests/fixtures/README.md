# Terraform test fixtures

`terraform-1.13.3-first-plan.json` was captured on 2026-10-06 using the official Terraform 1.13.3 Linux amd64 binary (verified against its published SHA256SUMS), with this isolated local configuration:

```hcl
resource "terraform_data" "fixture" {
  input = "synthetic-local-only"
}
```

After `terraform init -backend=false`, `tfops plan --save-plan reviewed.tfplan` generated the saved plan; `terraform show -json reviewed.tfplan` produced this fixture. No external provider or cloud infrastructure is involved. First provisioning legitimately omits `prior_state` and empty `resource_drift`. The regression test passes this real output through the apply guard with a fake apply delegate. The same saved plan was also successfully applied using the real wrapper and CLI in the isolated temporary directory.
