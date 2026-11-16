# GeldApp Homebrew tap

This tap distributes the GeldApp macOS preview as a Homebrew Cask.

After the first app release is published and its generated cask update has merged:

```sh
brew install --cask geldapp/tap/geldapp
brew upgrade --cask geldapp
brew uninstall --cask geldapp
```

The cask uses a versioned GitHub release DMG URL and the SHA-256 checksum published with that DMG. The app is a universal binary for Apple Silicon and Intel. Uninstall removes the app and preserves the user's local vault.

The preview is ad-hoc signed and unnotarized, with no Apple Developer ID signature. Homebrew does not bypass macOS quarantine; Gatekeeper may require the user to approve the first launch in Finder. GeldApp remains a prototype. Use sample data only. Signed-app Keychain access, physical Touch ID prompts, and Windows behavior have not been verified.

An hourly workflow checks the public GeldApp releases. A new cask can take up to an hour to appear, plus time for validation and auto-merge. When it finds a new stable release with a matching DMG and checksum, it opens or updates a cask pull request, dispatches cask validation on that PR's exact branch, and enables squash auto-merge. It needs no credential in the app repository.
