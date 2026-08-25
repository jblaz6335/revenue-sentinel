# Security and responsible-action boundary

Revenue Sentinel is designed to reduce false certainty and unsafe side effects in autonomous revenue operations.

## Controls

- Strict request schemas reject unknown fields and cap values, list sizes, and text length.
- Opportunity titles, notes, and evidence strings are untrusted data. They never become model or shell instructions.
- The model receives no payment, messaging, browser, wallet, deployment, or account-mutation tool.
- Deadline, eligibility, source validity, dust value, and action-gate rules are deterministic.
- Missing facts remain unknown rather than defaulting to approval.
- Every audit includes a canonical evidence digest.
- No credentials, buyer data, or personal information are stored in the repository. Public deployment identifiers are documented for reproducibility.
- Cloud configuration uses Application Default Credentials and is intended for a dedicated least-privilege service account.

## Not a security scanner

This is an opportunity-governance proof, not a vulnerability scanner, identity provider, escrow service, legal determination, financial adviser, payment processor, or guarantee of platform safety. Operators must verify applicable rules, eligibility, ownership, consent, payment protection, tax obligations, and account permissions.

## Reporting

Do not include secrets or personal data in a report. Describe the affected component, impact, and reproducible steps using synthetic data.
