#!/usr/bin/env python3
"""seal-verify — the PUBLIC verifier for Delimit Seal receipts (open-core).

Given a receipt, the published constitution-of-record, and the published Ed25519
public key, this checks — with **NO access to the engine, the detectors, or the
signing key** — that:

  1. content-pin:  the receipt's `layer0_seed_id` matches the published
     constitution (so a published v1 cannot mask a secretly-enforced v2);
  2. constitution self-consistency: the published constitution's stated seed id
     actually equals the hash of its own rules;
  3. signature:    the receipt's Ed25519 signature is valid under the public key;
  4. well-formed:  the receipt carries the required fields + does_not_attest.

It is honest by design: it prints what it does NOT establish. Dependencies:
`cryptography` + the published public key + published constitution. That's all —
no proprietary module is imported.
"""

import argparse
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_CONSTITUTION = os.path.join(_DIR, "docs", "layer0_seed.ratified.json")
_DEFAULT_PUBKEY = os.path.join(_DIR, "public", "seal_pubkey.ed25519")


def seed_id_from_rules(frozen_rules):
    payload = json.dumps(
        [{k: r[k] for k in ("id", "title", "severity", "clause")}
         for r in frozen_rules],
        sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical(obj):
    body = {k: v for k, v in obj.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


def _verify_sig(pub_hex, data, sig):
    if not isinstance(sig, str) or not sig.startswith("ed25519:"):
        return False
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex)).verify(
            bytes.fromhex(sig.split(":", 1)[1]), data)
        return True
    except Exception:
        return False


def verify_receipt(receipt, constitution, pub_hex):
    """Returns (verdict_bool, checks_dict, does_not_attest_dict)."""
    pub_seed = constitution.get("layer0_seed_id")
    recomputed = seed_id_from_rules(constitution.get("frozen_rules", []))
    checks = {
        "constitution_self_consistent": recomputed == pub_seed,
        "receipt_pinned_to_constitution":
            receipt.get("layer0_seed_id") == pub_seed == recomputed,
        "receipt_signature_valid":
            _verify_sig(pub_hex, _canonical(receipt), receipt.get("signature", "")),
        "receipt_well_formed":
            all(k in receipt for k in
                ("schema", "layer0_seed_id", "transcript_hash", "action"))
            and isinstance(receipt.get("does_not_attest"), dict),
    }
    if "signature" in constitution:  # the published constitution is self-verifying
        checks["constitution_signature_valid"] = _verify_sig(
            pub_hex, _canonical(constitution), constitution["signature"])
    verdict = all(checks.values())
    return verdict, checks, receipt.get("does_not_attest", {})


def main(argv=None):
    p = argparse.ArgumentParser(description="seal-verify (public Delimit Seal verifier)")
    p.add_argument("receipt", help="path to a receipt JSON file")
    p.add_argument("--constitution", default=_DEFAULT_CONSTITUTION,
                   help="published constitution-of-record (layer0_seed.ratified.json)")
    p.add_argument("--pubkey", default=_DEFAULT_PUBKEY,
                   help="published Ed25519 public key (hex)")
    args = p.parse_args(argv)

    receipt = json.load(open(args.receipt, encoding="utf-8"))
    constitution = json.load(open(args.constitution, encoding="utf-8"))
    pub_hex = open(args.pubkey, encoding="utf-8").read().strip()

    verdict, checks, dna = verify_receipt(receipt, constitution, pub_hex)

    print(f"seal-verify: {'✅ VERIFIED' if verdict else '❌ FAILED'}  "
          f"(product={receipt.get('product')}, seed={receipt.get('layer0_seed_id','')[:23]}…)")
    for name, ok in checks.items():
        print(f"  [{'✓' if ok else '✗'}] {name}")
    print("  what seal-verify does NOT establish (from the receipt's does_not_attest):")
    for k, v in dna.items():
        if v is True:
            print(f"    – {k}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
