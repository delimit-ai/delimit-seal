# Changelog

All notable changes to Delimit Seal (open-core public layer). The Layer-0 core is
content-hashed and signed; see [`CONSTITUTION.md`](CONSTITUTION.md).

## [0.2.0] - 2026-06-03

### Added
- Layer-0 procedural core: six fixed, content-hashed rules (L0.1–L0.6) — non-fabrication,
  no personhood/consciousness claims, authority-transfer refusal, mandatory deferral on
  non-delegable decisions, anti-manipulation, and no-secret-emission.
- Public **`seal-verify`**: verifies a receipt's content-pin, Ed25519 signature, and
  structure with no access to the engine or the signing key.
- Signed, content-hashed constitution-of-record (`docs/layer0_seed.ratified.json`).

### Security
- Receipts are signed asymmetrically (Ed25519); the public key is published and the
  signing key is held server-side. Secrets detected by L0.6 are redacted, never persisted.
