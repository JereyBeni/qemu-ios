#!/usr/bin/env python3
"""Inspect an iPhone4,1 IPSW for N94AP DeviceTree research.

This tool inventories the IPSW ZIP and BuildManifest. It does not decrypt IMG3
payloads, extract firmware keys, or modify the input archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import sys
import zipfile
from pathlib import Path
from typing import Any

PRODUCT_TYPE = "iPhone4,1"
BOARD = "n94ap"


def read_build_manifest(archive: zipfile.ZipFile) -> dict[str, Any]:
    try:
        data = archive.read("BuildManifest.plist")
    except KeyError as exc:
        raise ValueError("BuildManifest.plist is missing from the IPSW") from exc

    manifest = plistlib.loads(data)
    if not isinstance(manifest, dict):
        raise ValueError("BuildManifest.plist root is not a dictionary")
    return manifest


def identity_summary(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    identities = manifest.get("BuildIdentities", [])
    if not isinstance(identities, list):
        return summaries

    for index, identity in enumerate(identities):
        if not isinstance(identity, dict):
            continue
        info = identity.get("Info", {})
        if not isinstance(info, dict):
            info = {}
        manifest_entries = identity.get("Manifest", {})
        if not isinstance(manifest_entries, dict):
            manifest_entries = {}
        device_tree_entry = manifest_entries.get("DeviceTree", {})
        if not isinstance(device_tree_entry, dict):
            device_tree_entry = {}
        device_tree_info = device_tree_entry.get("Info", {})
        if not isinstance(device_tree_info, dict):
            device_tree_info = {}
        summaries.append({
            "index": index,
            "product_type": info.get("ProductType"),
            "device_class": info.get("DeviceClass"),
            "board_config": info.get("BoardConfig"),
            "variant": info.get("Variant"),
            "restore_behavior": info.get("RestoreBehavior"),
            "device_tree_path": device_tree_info.get("Path"),
            "device_tree_digest": device_tree_info.get("Digest"),
        })
    return summaries


def find_device_tree(archive: zipfile.ZipFile) -> list[str]:
    matches = []
    for name in archive.namelist():
        leaf = name.rsplit("/", 1)[-1].lower()
        if leaf in {
            "devicetree.n94ap.img3",
            "devicetree.n94ap.im4p",
            "devicetree.n94ap.img4",
        }:
            matches.append(name)
    return sorted(matches)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an iPhone 4S IPSW and locate its N94AP DeviceTree."
    )
    parser.add_argument("ipsw", type=Path, help="Path to the locally obtained IPSW")
    parser.add_argument(
        "--extract-to",
        type=Path,
        help="Optionally copy the DeviceTree container (still possibly encrypted) here",
    )
    args = parser.parse_args()

    if not args.ipsw.is_file():
        parser.error(f"IPSW does not exist: {args.ipsw}")

    try:
        with zipfile.ZipFile(args.ipsw) as archive:
            manifest = read_build_manifest(archive)
            identities = identity_summary(manifest)
            matches = find_device_tree(archive)
            manifest_paths = [
                item["device_tree_path"] for item in identities
                if item["device_tree_path"] and item["product_type"] == PRODUCT_TYPE
            ]
            if manifest_paths:
                matches = sorted(set(manifest_paths) & set(archive.namelist())) or matches

            report: dict[str, Any] = {
                "ipsw": args.ipsw.name,
                "product_version": manifest.get("ProductVersion"),
                "build_version": manifest.get("ProductBuildVersion"),
                "target": PRODUCT_TYPE,
                "board": BOARD,
                "matching_build_identities": [
                    item for item in identities
                    if item["product_type"] == PRODUCT_TYPE
                    or item["device_class"] == BOARD
                    or item["board_config"] == BOARD
                ],
                "device_tree_candidates": [],
                "note": (
                    "The extracted IMG3/IM4P may still be encrypted or wrapped. "
                    "This script does not decrypt firmware."
                ),
            }

            for name in matches:
                payload = archive.read(name)
                report["device_tree_candidates"].append({
                    "archive_path": name,
                    "size_bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })

            if args.extract_to:
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected exactly one N94AP DeviceTree, found {len(matches)}"
                    )
                args.extract_to.parent.mkdir(parents=True, exist_ok=True)
                args.extract_to.write_bytes(archive.read(matches[0]))
                report["extracted_container"] = str(args.extract_to)

            print(json.dumps(report, indent=2))
            if not report["matching_build_identities"]:
                print(
                    "warning: no BuildIdentity explicitly matched iPhone4,1/n94ap",
                    file=sys.stderr,
                )
            if not matches:
                print("error: N94AP DeviceTree was not found in the IPSW", file=sys.stderr)
                return 2
            return 0

    except (OSError, zipfile.BadZipFile, plistlib.InvalidFileException, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
