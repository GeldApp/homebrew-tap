#!/usr/bin/env python3
"""Validate a public app release before its metadata is used to write a cask."""

import json
import pathlib
import re
import sys


SEMVER = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z")


def prepare_release(release: dict) -> dict:
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("Only published stable releases can create a cask")
    if release.get("immutable") is not True:
        raise ValueError("Only immutable published releases can create a cask")

    tag = release.get("tag_name", "")
    match = SEMVER.fullmatch(tag)
    if not match:
        raise ValueError(f"Refusing non-stable release tag: {tag!r}")
    version = tag[1:]
    dmg_name = f"GeldApp-{version}-macos-universal.dmg"
    checksum_name = f"{dmg_name}.sha256"
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Release assets must be a list")

    asset_urls = {}
    asset_digests = {}
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("Release contains malformed asset metadata")
        asset_name = asset.get("name")
        if asset_name in {dmg_name, checksum_name}:
            asset_urls[asset_name] = asset.get("browser_download_url")
            asset_digests[asset_name] = asset.get("digest")

    expected_dmg_url = f"https://github.com/GeldApp/GeldApp/releases/download/{tag}/{dmg_name}"
    expected_checksum_url = f"https://github.com/GeldApp/GeldApp/releases/download/{tag}/{checksum_name}"
    if asset_urls.get(dmg_name) != expected_dmg_url:
        raise ValueError(f"Release {tag} lacks the expected versioned DMG asset")
    if asset_urls.get(checksum_name) != expected_checksum_url:
        raise ValueError(f"Release {tag} lacks the matching versioned checksum asset")

    return {
        "tag": tag,
        "version": version,
        "dmg_name": dmg_name,
        "dmg_url": expected_dmg_url,
        "checksum_url": expected_checksum_url,
        "api_digest": asset_digests.get(dmg_name),
    }


def main() -> None:
    release = json.loads(pathlib.Path(sys.argv[1]).read_text())
    prepared = prepare_release(release)
    pathlib.Path(sys.argv[2]).write_text(json.dumps(prepared))


if __name__ == "__main__":
    main()
