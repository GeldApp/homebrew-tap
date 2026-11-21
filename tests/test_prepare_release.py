import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from scripts.prepare_release import IncompatibleRelease, prepare_release


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "prepare_release.py"
WORKFLOW = pathlib.Path(__file__).parents[1] / ".github" / "workflows" / "update-cask.yml"


def release_fixture():
    tag = "v0.2.1"
    dmg = "GeldApp-0.2.1-macos-universal.dmg"
    checksum = f"{dmg}.sha256"
    base = f"https://github.com/GeldApp/GeldApp/releases/download/{tag}"
    return {
        "draft": False,
        "prerelease": False,
        "immutable": True,
        "tag_name": tag,
        "assets": [
            {"name": dmg, "browser_download_url": f"{base}/{dmg}"},
            {"name": checksum, "browser_download_url": f"{base}/{checksum}"},
        ],
    }


class PrepareReleaseTests(unittest.TestCase):
    def test_accepts_published_stable_release_with_matching_assets(self):
        prepared = prepare_release(release_fixture())
        self.assertEqual(prepared["version"], "0.2.1")
        self.assertEqual(prepared["tag"], "v0.2.1")
        self.assertTrue(prepared["dmg_url"].endswith("GeldApp-0.2.1-macos-universal.dmg"))

    def test_rejects_draft_prerelease_and_mutable_release(self):
        for field, value in (("draft", True), ("prerelease", True)):
            release = release_fixture()
            release[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                prepare_release(release)

        mutable_release = release_fixture()
        mutable_release["immutable"] = False
        with self.assertRaises(IncompatibleRelease):
            prepare_release(mutable_release)

    def test_rejects_release_without_immutable_metadata(self):
        release = release_fixture()
        del release["immutable"]
        with self.assertRaisesRegex(IncompatibleRelease, "immutable"):
            prepare_release(release)

    def test_rejects_unstable_or_unsafe_tag(self):
        for tag in ("v1.2", "v1.2.3-beta.1", 'v1.2.3"; system("echo unsafe")'):
            release = release_fixture()
            release["tag_name"] = tag
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                prepare_release(release)

    def test_rejects_missing_dmg_or_checksum(self):
        for missing_name in ("GeldApp-0.2.1-macos-universal.dmg", "GeldApp-0.2.1-macos-universal.dmg.sha256"):
            release = release_fixture()
            release["assets"] = [asset for asset in release["assets"] if asset["name"] != missing_name]
            with self.subTest(missing_name=missing_name), self.assertRaises(IncompatibleRelease):
                prepare_release(release)

    def test_legacy_release_exit_status_and_workflow_gates_skip_later_steps(self):
        release = release_fixture()
        release["immutable"] = False
        source = WORKFLOW.read_text()
        with self.subTest(kind="mutable"):
            self.assert_incompatible_cli(release)

        release = release_fixture()
        release["assets"] = []
        with self.subTest(kind="missing assets"):
            self.assert_incompatible_cli(release)

        invalid_release = release_fixture()
        invalid_release["assets"][0]["browser_download_url"] = "https://github.com/GeldApp/GeldApp/releases/latest/download/app.dmg"
        with self.subTest(kind="invalid URL"):
            result, output_exists = self.run_cli(invalid_release)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(output_exists)

        self.assertIn("id: release", source)
        self.assertIn("validation_status=$?", source)
        self.assertIn('echo \'available=false\' >> "$GITHUB_OUTPUT"', source)
        gated_steps = (
            "Read and verify the DMG checksum",
            "Write the exact-version cask",
            "Create or update the cask pull request",
            "Dispatch cask checks on the PR branch",
            "Enable squash auto-merge after required checks",
        )
        for name in gated_steps:
            marker = f"- name: {name}"
            start = source.index(marker)
            next_step = source.find("\n      - name:", start + len(marker))
            block = source[start:] if next_step < 0 else source[start:next_step]
            with self.subTest(step=name):
                self.assertIn("steps.release.outputs.available == 'true'", block)

    def assert_incompatible_cli(self, release):
        result, output_exists = self.run_cli(release)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(output_exists)

    @staticmethod
    def run_cli(release):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            input_path = root / "release.json"
            output_path = root / "release-asset.json"
            input_path.write_text(json.dumps(release))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            return result, output_path.exists()

    def test_rejects_asset_urls_outside_the_exact_versioned_release(self):
        release = release_fixture()
        release["assets"][0]["browser_download_url"] = "https://github.com/GeldApp/GeldApp/releases/latest/download/app.dmg"
        with self.assertRaisesRegex(ValueError, "versioned DMG"):
            prepare_release(release)


if __name__ == "__main__":
    unittest.main()
