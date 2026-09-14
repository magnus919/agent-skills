# Provenance, rights, and dataset release

Every batch needs a source identifier, collection or snapshot time, license or
consent basis, transformation history, data classification, access policy,
retention/deletion path, guide version, and content hash or immutable revision.
Record exclusions and missingness instead of silently dropping them.

Before release, verify that annotations may be used for the named downstream
purpose, that sensitive fields are minimized, and that deletion requests can be
propagated to derived labels and exports. Route storage, lineage, and deletion
execution to `data-engineering`; this reference defines the evidence the
annotation owner must hand off.
