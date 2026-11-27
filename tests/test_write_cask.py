import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "write_cask.py"


class WriteCaskTests(unittest.TestCase):
    def invoke(self, asset, checksum, dmg_bytes=b"verified dmg"):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = pathlib.Path(temporary.name)
        asset_path = root / "asset.json"
        checksum_path = root / "release.sha256"
        output_path = root / "Casks" / "geldapp.rb"
        dmg_path = root / "GeldApp.dmg"
        dmg_path.write_bytes(dmg_bytes)
        asset_path.write_text(json.dumps(asset))
        checksum_path.write_text(checksum)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(asset_path), str(checksum_path), str(output_path), str(dmg_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, output_path

    def test_writes_exact_tag_url_and_checksum_without_destructive_zap(self):
        name = "GeldApp-0.2.1-macos-universal.dmg"
        dmg_bytes = b"verified dmg"
        digest = hashlib.sha256(dmg_bytes).hexdigest()
        result, output = self.invoke(
            {
                "tag": "v0.2.1",
                "version": "0.2.1",
                "dmg_name": name,
                "dmg_url": f"https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}",
                "api_digest": f"sha256:{digest}",
            },
            f"{digest}  {name}\n",
            dmg_bytes,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        cask = output.read_text()
        self.assertTrue(cask.startswith("# frozen_string_literal: true\n"))
        self.assertIn(f'version "0.2.1"', cask)
        self.assertIn(f'sha256 "{digest}"', cask)
        url_line = next(line for line in cask.splitlines() if line.startswith('  url '))
        url_template = url_line.removeprefix('  url "').removesuffix('"')
        self.assertEqual(
            url_template,
            "https://github.com/GeldApp/GeldApp/releases/download/v#{version}/GeldApp-#{version}-macos-universal.dmg",
        )
        self.assertEqual(
            url_template.replace("#{version}", "0.2.1"),
            f"https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}",
        )
        self.assertIn('app "GeldApp.app"', cask)
        self.assertIn('depends_on macos: :ventura', cask)
        self.assertIn('caveats "Requires macOS 13.3 or later. The app cannot launch on macOS 13.0 through 13.2."', cask)
        self.assertNotIn("preflight", cask)
        self.assertNotIn(":no_check", cask)
        self.assertNotIn("zap", cask)

    def test_rejects_checksum_for_another_asset(self):
        name = "GeldApp-0.2.1-macos-universal.dmg"
        result, output = self.invoke(
            {
                "tag": "v0.2.1",
                "version": "0.2.1",
                "dmg_name": name,
                "dmg_url": f"https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}",
            },
            f"{'a' * 64}  different.dmg\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_rejects_non_versioned_release_url(self):
        name = "GeldApp-0.2.1-macos-universal.dmg"
        result, output = self.invoke(
            {
                "tag": "v0.2.1",
                "version": "0.2.1",
                "dmg_name": name,
                "dmg_url": "https://github.com/GeldApp/GeldApp/releases/latest/download/geldapp.dmg",
            },
            f"{'a' * 64}  {name}\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_rejects_mismatched_downloaded_dmg_and_api_digest(self):
        name = "GeldApp-0.2.1-macos-universal.dmg"
        checksum = f"{'a' * 64}  {name}\n"
        asset = {
            "tag": "v0.2.1",
            "version": "0.2.1",
            "dmg_name": name,
            "dmg_url": f"https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}",
        }
        result, output = self.invoke(asset, checksum, b"different bytes")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

        matching = hashlib.sha256(b"verified dmg").hexdigest()
        result, output = self.invoke(
            {**asset, "api_digest": f"sha256:{'b' * 64}"},
            f"{matching}  {name}\n",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_rejects_unsafe_version_text(self):
        name = 'GeldApp-0.2.1\"; system("echo unsafe")-macos-universal.dmg'
        result, output = self.invoke(
            {
                "tag": "v0.2.1\"; system(\"echo unsafe\")",
                "version": '0.2.1\"; system("echo unsafe")',
                "dmg_name": name,
                "dmg_url": "https://github.com/GeldApp/GeldApp/releases/download/unsafe/unsafe.dmg",
            },
            f"{'a' * 64}  {name}\n",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
