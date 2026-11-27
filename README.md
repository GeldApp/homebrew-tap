# GeldApp Homebrew tap

This tap distributes the GeldApp macOS preview as a Homebrew Cask.

After the first app release is published and its generated cask update has merged:

```sh
brew install --cask geldapp/tap/geldapp
brew upgrade --cask geldapp
brew uninstall --cask geldapp
```

The cask uses a versioned GitHub release DMG URL and the SHA-256 checksum published with that DMG. The app is a universal binary for Apple Silicon and Intel. Uninstall removes the app and preserves the user's local vault.

GeldApp requires macOS 13.3 or later. Homebrew's cask DSL can declare a minimum macOS major release, so this cask requires Ventura (macOS 13) and cannot encode the 13.3 minor-version floor. The app bundle's Launch Services minimum rejects launches on macOS 13.0 through 13.2.

The preview is ad-hoc signed and unnotarized, with no Apple Developer ID signature. Homebrew does not bypass macOS quarantine; Gatekeeper may require the user to approve the first launch in Finder. GeldApp remains a prototype. Use sample data only. Signed-app Keychain access, physical Touch ID prompts, and Windows behavior have not been verified.

The GeldApp release workflow attempts guarded publication each Monday at 08:00 UTC after its checks pass ([release policy](https://github.com/GeldApp/GeldApp/blob/main/docs/ci-release.md#draft-and-weekly-release-behavior)). The tap checks public releases hourly, so it can take up to an hour to detect a compatible release. It skips legacy or incompatible releases until an immutable stable release includes the expected universal DMG and matching checksum. When it finds one, it opens or updates a cask pull request, dispatches a diagnostic audit for that PR branch, and enables squash auto-merge.

Because the updater creates or updates the PR with `GITHUB_TOKEN`, GitHub places the resulting `pull_request` Actions run in an approval-required state. A maintainer with write access must approve that PR run. After the required `Cask audit` check succeeds, squash auto-merge can complete. The separately dispatched `workflow_dispatch` audit is diagnostic only: GitHub does not count its checks toward a PR's required status checks, even when it tests the exact head commit ([`GITHUB_TOKEN` workflow approvals](https://docs.github.com/en/actions/concepts/security/github_token), [required-check event rules](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks#checks-from-some-workflow-jobs-are-not-evaluated)). The PR audit checks the exact checkout SHA and verifies the downloaded DMG against its declared SHA-256.
