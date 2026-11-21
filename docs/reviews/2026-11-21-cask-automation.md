# Cask automation source review

- Reviewed source: `781bc4c8eb5c490034c11c8745a76193a4d668b1`.
- Independent reviewer: Terra. Verdict: approved for draft PR and hosted validation; no blocking source finding remains. All 12 Python tests were independently run successfully.
- Fixed findings: use the registered exact PR checkout for fully qualified Homebrew audit; compare checkout SHA and cask contents; verify downloaded DMG bytes against checksum and available GitHub digest; require immutable release metadata; dispatch checks only for an existing matching PR; reject head drift; gate every update step on the same compatibility output.
- Hourly polling is retained. Legacy releases without compatible immutable assets skip before cask generation; malformed metadata fails closed. No placeholder cask or unchecked digest is published.
- Worker actionlint, Python syntax, YAML parsing and whitespace checks passed. The cask preserves vault data on uninstall and does not bypass quarantine.
- Hosted Homebrew audit, first generated cask and actual installation remain unverified. They require the first compatible immutable app release.
- Final metadata-only head review and the protected Cask audit check remain merge conditions.
