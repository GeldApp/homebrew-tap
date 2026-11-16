import unittest

from scripts.prepare_release import prepare_release


def release_fixture():
    tag = "v0.2.1"
    dmg = "GeldApp-0.2.1-macos-universal.dmg"
    checksum = f"{dmg}.sha256"
    base = f"https://github.com/GeldApp/GeldApp/releases/download/{tag}"
    return {
        "draft": False,
        "prerelease": False,
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

    def test_rejects_draft_and_prerelease(self):
        for field in ("draft", "prerelease"):
            release = release_fixture()
            release[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
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
            with self.subTest(missing_name=missing_name), self.assertRaises(ValueError):
                prepare_release(release)

    def test_rejects_asset_urls_outside_the_exact_versioned_release(self):
        release = release_fixture()
        release["assets"][0]["browser_download_url"] = "https://github.com/GeldApp/GeldApp/releases/latest/download/app.dmg"
        with self.assertRaisesRegex(ValueError, "versioned DMG"):
            prepare_release(release)


if __name__ == "__main__":
    unittest.main()
