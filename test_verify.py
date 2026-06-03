"""Public smoke test: the bundled sample receipt verifies, and a tampered one fails.
Run:  python -m pytest -q   (or: python -m unittest)
"""

import json
import os
import unittest

import seal_verify

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(rel):
    with open(os.path.join(_HERE, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _pubkey():
    with open(os.path.join(_HERE, "public", "seal_pubkey.ed25519"), encoding="utf-8") as fh:
        return fh.read().strip()


class TestSealVerify(unittest.TestCase):
    def setUp(self):
        self.receipt = _load("examples/sample_receipt.json")
        self.constitution = _load("docs/layer0_seed.ratified.json")
        self.pub = _pubkey()

    def test_sample_receipt_verifies(self):
        verdict, checks, _ = seal_verify.verify_receipt(self.receipt, self.constitution, self.pub)
        self.assertTrue(verdict, checks)
        self.assertTrue(checks["receipt_pinned_to_constitution"])
        self.assertTrue(checks["receipt_signature_valid"])

    def test_tampered_receipt_fails(self):
        bad = dict(self.receipt)
        bad["action"] = "TAMPERED"
        verdict, checks, _ = seal_verify.verify_receipt(bad, self.constitution, self.pub)
        self.assertFalse(verdict)
        self.assertFalse(checks["receipt_signature_valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
