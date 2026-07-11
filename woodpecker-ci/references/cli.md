# CLI reference and local execution

The CLI surface changes between releases. Use the installed binary as the first authority:

```bash
woodpecker-cli --help
woodpecker-cli <command> --help
```

## Useful workflow

```bash
# Check the workflow before pushing
woodpecker-cli lint .woodpecker.yml

# Execute locally when the supported backend is available
woodpecker-cli exec .woodpecker.yml

# Inspect available repository operations
woodpecker-cli repo --help
woodpecker-cli pipeline --help
woodpecker-cli log --help

# Add a file-backed repository secret
woodpecker-cli repo secret add \
  --repository OWNER/REPO \
  --name deploy-key \
  --value @/secure/path/deploy-key
```

The official CLI documentation also exposes flags for setting pipeline metadata during local execution, including event, branch, changed files, commit SHA, and forge URL. Use `woodpecker-cli exec --help` for the exact installed names.

## Local execution limits

Local execution is valuable for command scripts, syntax, and metadata conditions. It does not automatically reproduce:

- the server's repository/organization/global secret lookup;
- forge webhook payloads and permissions;
- server-side plugin and secret filters;
- the exact agent labels and backend;
- production network policy or registry credentials.

Use a real non-secret pipeline after local checks pass. Never add a workaround for secrets based on an old issue or remembered flag without checking the current CLI help.