# Controller credential provisioning

No credential belongs in this public repository, a PR, an Actions secret, a job
container, a screenshot, command output, or chat. Existing desktop authentication
must not be copied to the hosts. Provision only after the exact repository
administration scope is authorized.

## Smallest supported route: fine-grained PAT

The current controller reads a host-only bearer-token file before each API call.
Use GitHub's supported signed-in **Settings → Developer settings → Personal
access tokens → Fine-grained tokens → Generate new token** flow. A normal `gh`
OAuth login cannot mint a fine-grained PAT through the public REST API.

For independent revocation, create one token per controller:

- Names: `agent-skills-ci-saru` and `agent-skills-ci-gpuslut01`.
- Resource owner: `magnus919`.
- Repository access: **Only select repositories → agent-skills**.
- Repository permissions: **Administration: Read and write**; Metadata read is
  implicit. Leave all other repository/account/organization permissions ungranted.
- Use an explicit expiration (30 days is a reasonable initial operating limit)
  and record the rotation owner/date outside CI.

GitHub requires Administration:write to create a repository registration token;
there is no repository runner-only permission. These tokens can administer this
repository, so selection is a repository boundary, not an operation boundary.

Browser authentication, 2FA/passkeys, and any new credential entry/confirmation
must use the user handoff. Do not ask the user to paste a token into chat. After
creation, have the user save it through a secure local handoff (for example a
mode-0600 local file outside the checkout); do not print it. Transfer each token
over the existing authorized SSH connection only to its matching host at
`~/.config/agent-skills-ci/controller-token`, directory mode 0700/file mode 0600,
owned by the controller user. Remove the temporary handoff copy after verified
transfer. Do not place credentials in Docker environment variables or arguments.

The controller obtains one-hour registration tokens and passes them through stdin
into fresh single-job workers. The durable PAT remains outside the worker. Test
only the exact runner API capabilities needed, without printing response tokens.

## GitHub App alternative

GitHub recommends an App for a long-lived integration. Register/install a private
App on only `magnus919/agent-skills` with repository Administration:write and
implicit Metadata read, with all unrelated permissions disabled. A host-only
broker signs an App JWT and requests installation tokens restricted to that repo
and permission; those tokens expire after one hour. Keep the signing private key
outside jobs and host-accessible only to the broker.

The current controller can read the resulting bearer file, but **does not yet
implement App JWT signing or installation-token renewal**. Choosing this route
requires a reviewed broker/renewal implementation; copying one installation token
into the file is not continuous provisioning. An App avoids user-token lifetime
coupling but does not remove the required Administration:write permission.

## Activation after provisioning

Install the reviewed public-service deny list in the configured host-only path.
Use immutable image IDs in the service's command. Verify ephemeral registration,
real single-job execution/replacement, exact-identity cleanup, timeout/guard failure,
and both deterministic workflows before requesting PR merge. Preserve existing
external-contributor approvals. Do not rerun/cancel existing work without explicit
instruction. Keep the existing GPU evaluator and other runner pools separate.

Sources: [GitHub runner registration API](https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository),
[fine-grained token management](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens),
[App installation-token flow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app).
