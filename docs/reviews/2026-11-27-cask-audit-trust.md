# Cask trust review

Luna implemented `d43d2c1a967894dc21491f3bfaf0b1b47b9cc426` and Terra approved it against main `1f6c0b9f159446c88f0ff349cd8b8ba24afd3875`.

The first real cask passed style but Homebrew refused to audit it before it was trusted. CI now trusts only `geldapp/tap/geldapp` in a runner-temporary configuration directory after confirming the tap checkout SHA and cask bytes. Strict audit, fetch and checksum verification remain required.

Independent actionlint, git diff and 12 Python tests passed. The final commit still requires the protected check before squash merge. The first generated cask must pass the updated hosted audit before its own merge.

Terra also approved `56461c3e6884c12c27428dd384a8bb28d8aa2806`. The first strict audit after scoped trust treated the hard-coded asset URL as unversioned. The generator now uses Homebrew's version interpolation, verifies that it resolves to the same immutable asset URL and keeps the literal checksum. The real v0.3.0 cask passed strict local audit. Independent fixture tests, actionlint and diff checks passed.
