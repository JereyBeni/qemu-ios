import io
import plistlib
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "n94"))

import inspect_ipsw


class InspectIPSWTests(unittest.TestCase):
    def make_archive(self):
        manifest = {
            "ProductVersion": "5.1.1",
            "ProductBuildVersion": "9B206",
            "BuildIdentities": [{
                "Info": {
                    "ProductType": "iPhone4,1",
                    "DeviceClass": "n94ap",
                    "BoardConfig": "n94ap",
                },
                "Manifest": {
                    "DeviceTree": {
                        "Info": {
                            "Path": "Firmware/all_flash/all_flash.n94ap.production/DeviceTree.n94ap.img3",
                            "Digest": b"test-digest",
                        }
                    }
                },
            }],
        }
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("BuildManifest.plist", plistlib.dumps(manifest))
            archive.writestr(
                "Firmware/all_flash/all_flash.n94ap.production/DeviceTree.n94ap.img3",
                b"synthetic-img3",
            )
        return buffer.getvalue()

    def test_reads_n94_identity_and_manifest_device_tree_path(self):
        with zipfile.ZipFile(io.BytesIO(self.make_archive())) as archive:
            manifest = inspect_ipsw.read_build_manifest(archive)
            identities = inspect_ipsw.identity_summary(manifest)
            self.assertEqual(manifest["ProductBuildVersion"], "9B206")
            self.assertEqual(identities[0]["product_type"], "iPhone4,1")
            self.assertEqual(identities[0]["board_config"], "n94ap")
            self.assertEqual(
                identities[0]["device_tree_path"],
                "Firmware/all_flash/all_flash.n94ap.production/DeviceTree.n94ap.img3",
            )

    def test_locates_n94_device_tree_and_ignores_other_boards(self):
        with zipfile.ZipFile(io.BytesIO(self.make_archive())) as archive:
            paths = inspect_ipsw.find_device_tree(archive)
            self.assertEqual(len(paths), 1)
            self.assertTrue(paths[0].endswith("DeviceTree.n94ap.img3"))


if __name__ == "__main__":
    unittest.main()
