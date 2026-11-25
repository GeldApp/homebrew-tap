#!/usr/bin/env python3
"""Write a cask only from a published, versioned release and its SHA-256 asset."""

import json
import hashlib
import pathlib
import re
import sys


def main() -> None:
    release_asset = json.loads(pathlib.Path(sys.argv[1]).read_text())
    checksum_text = pathlib.Path(sys.argv[2]).read_text().strip()
    output = pathlib.Path(sys.argv[3])
    dmg_path = pathlib.Path(sys.argv[4])

    version = release_asset["version"]
    tag = release_asset["tag"]
    dmg_name = release_asset["dmg_name"]
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise SystemExit("Release version must be stable three-part SemVer")
    expected_name = f"GeldApp-{version}-macos-universal.dmg"
    if tag != f"v{version}" or dmg_name != expected_name:
        raise SystemExit("Release tag and DMG name do not match the version")

    match = re.fullmatch(rf"([0-9a-fA-F]{{64}})  {re.escape(dmg_name)}", checksum_text)
    if not match:
        raise SystemExit("Checksum asset must contain one SHA-256 line for the exact DMG name")
    sha256 = match.group(1).lower()
    actual_sha256 = hashlib.sha256(dmg_path.read_bytes()).hexdigest()
    if actual_sha256 != sha256:
        raise SystemExit("Downloaded DMG does not match the published checksum asset")

    api_digest = release_asset.get("api_digest")
    if api_digest is not None and api_digest != f"sha256:{actual_sha256}":
        raise SystemExit("Downloaded DMG does not match the GitHub release asset digest")

    expected_url = f"https://github.com/GeldApp/GeldApp/releases/download/{tag}/{dmg_name}"
    if release_asset["dmg_url"] != expected_url:
        raise SystemExit("DMG URL does not point to its immutable versioned release asset")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "# frozen_string_literal: true",
                "",
                'cask "geldapp" do',
                f'  version "{version}"',
                f'  sha256 "{sha256}"',
                "",
                f'  url "{expected_url}"',
                '  name "GeldApp"',
                '  desc "Personal finance workspace"',
                '  homepage "https://github.com/GeldApp/GeldApp"',
                "",
                '  depends_on macos: :ventura',
                "",
                '  app "GeldApp.app"',
                "",
                '  caveats "Requires macOS 13.3 or later. The app cannot launch on macOS 13.0 through 13.2."',
                "end",
            ]
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
