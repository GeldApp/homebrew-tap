# Cask platform requirement review

- Implementation: Luna; independent adversarial reviewer: gpt-6.1-terra.
- Exact reviewed source: `c53fe0c75f10460f6e34d10de7ff35ac1d027aba`, compared with tap main `7511b1e70a566629e45d402e620e927a7d9d95e3`.
- Verdict: APPROVE, no blocking findings. Generator, fixture and docs only; release selection and validation gates remain unchanged.
- Standard Homebrew dependency gates Ventura (major macOS 13); a static cask caveat and README state the exact macOS 13.3 app requirement. Homebrew cannot enforce the minor version through this stanza; the bundle's Launch Services minimum rejects launch on 13.0–13.2. Unsupported Ruby preflight was omitted.
- Reviewer independently passed 12 Python fixture tests and diff checks. Worker passed generated cask Ruby syntax and Homebrew style checks.
- Strict audit, fetch and installation remain pending the first compatible real published DMG/cask. No synthetic release or checksum has been published, no quarantine behavior changed, and no runtime validation is claimed.
