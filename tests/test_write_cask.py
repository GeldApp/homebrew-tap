import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "write_cask.py"


class WriteCaskTests(unittest.TestCase):
    def invoke(self, asset, checksum):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = pathlib.Path(temporary.name)
        asset_path = root / "asset.json"
        checksum_path = root / "release.sha256"
        output_path = root / "Casks" / "geldapp.rb"
        asset_path.write_text(json.dumps(asset))
        checksum_path.write_text(checksum)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(asset_path), str(checksum_path), str(output_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, output_path

    def test_writes_exact_tag_url_and_checksum_without_destructive_zap(self):
        name = "GeldApp-0.2.1-macos-universal.dmg"
        digest = "a" * 64
        result, output = self.invoke(
            {
                "tag": "v0.2.1",
                "version": "0.2.1",
                "dmg_name": name,
                "dmg_url": f"https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}",
            },
            f"{digest}  {name}\n",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        cask = output.read_text()
        self.assertIn(f'version "0.2.1"', cask)
        self.assertIn(f'sha256 "{digest}"', cask)
        self.assertIn(f'url "https://github.com/GeldApp/GeldApp/releases/download/v0.2.1/{name}"', cask)
        self.assertIn('app "GeldApp.app"', cask)
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
