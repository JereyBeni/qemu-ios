# M0: N94AP firmware and DeviceTree evidence

**Milestone:** M0, evidence collection  
**Target:** iPhone4,1 / n94ap  
**Initial firmware:** iOS 5.1.1, build 9B206  
**Status:** firmware metadata verified; raw N94 DeviceTree has not yet been inspected in this worktree.

M0 is not complete until the raw Apple DeviceTree has been decoded and its values have been recorded with provenance. Product specifications and A4 register maps are not substitutes for N94 evidence.

## 1. Chosen firmware baseline

Use the iPhone 4S 9B206 IPSW as the first reproducible target:

| Field | Value |
|---|---|
| Filename | `iPhone4,1_5.1.1_9B206_Restore.ipsw` |
| Product type | `iPhone4,1` |
| iOS version | 5.1.1 |
| Build | 9B206 |
| Published size | 803 MiB |
| SHA-1 | `ac99928cc52fcb24502959ace3c36a63ba75ab6c` |
| SHA-256 | `b6870acf127a58e2775f93b9314cc678ac39caed7f0cbd13699f5f3a09c6f277` |

Source: [IPSW Downloads, iPhone4,1 / 9B206](https://ipsw.me/download/iPhone4,1/9B206/). The page records the filename, build, product identifier, size and checksums. This firmware is currently unsigned, which does not prevent offline research of a locally held IPSW.

Do not commit the IPSW, extracted firmware binaries, device-specific identifiers, firmware keys or personal data to this repository. Keep local artifacts outside the checkout, for example under `~/Developer/qemu-ios-files/n94/9B206/`.

## 2. Locate and inspect the DeviceTree

Apple's device tree is not a standard flattened Linux DTB. It is an Apple-specific binary tree packaged in an IMG3/IM4P container. The container may be encrypted, and the decryption material varies by firmware build. The parser below must receive a raw, decrypted Apple DeviceTree, not the IPSW ZIP entry or an encrypted IMG3 wrapper.

The expected N94 payload filename is `DeviceTree.n94ap.img3`. Apple firmware references for N94AP use this filename; the exact archive path should be confirmed from the selected 9B206 IPSW.

### 2.1 Verify the IPSW

PowerShell:

```powershell
$ipsw = "$HOME\Downloads\iPhone4,1_5.1.1_9B206_Restore.ipsw"
Get-FileHash $ipsw -Algorithm SHA256
```

The SHA-256 must match the value in the table above before treating the archive as the selected baseline.

### 2.2 Inventory the archive

From the repository root:

```powershell
python tools/n94/inspect_ipsw.py $ipsw --extract-to "$HOME\Developer\qemu-ios-files\n94\9B206\DeviceTree.n94ap.img3"
```

The helper reads `BuildManifest.plist`, reports matching BuildIdentity records, locates the N94AP DeviceTree entry, and records the extracted container's size and SHA-256. It does not decrypt or alter the IPSW. Keep the output JSON with the local research artifacts.

### 2.3 Decode the Apple DeviceTree

Use a parser that explicitly supports Apple's binary DeviceTree format. One small reference implementation is [bazad/devicetree-parse](https://github.com/bazad/devicetree-parse). Its documented input is a raw, unencrypted/unwrapped device-tree binary:

```sh
./devicetree-parse /path/to/raw-n94ap-devicetree
./devicetree-parse -v /path/to/raw-n94ap-devicetree > n94ap-9B206-device-tree.txt
```

The `ipsw` CLI also documents DeviceTree extraction with `ipsw extract --dtree`; see [its extraction guide](https://blacktop.github.io/ipsw/docs/guides/extract/). Confirm the produced file is raw and parseable before using it. If the extracted artifact remains an IMG3/IM4P container or is encrypted, stop at that point and use a build-matched IMG3 extraction/decryption workflow. Do not feed the wrapper to the binary-tree parser.

Apple DeviceTree format and IPSW location notes: [The Apple Wiki: DeviceTree](https://theapplewiki.com/wiki/DeviceTree).

## 3. Record only hardware-relevant properties

Inspect the decoded tree and record the following. Do not infer values from N90AP:

| Area | Properties to capture | Required evidence |
|---|---|---|
| Identity | `compatible`, `model`, board/chip identifiers | Exact node/property and raw value |
| Memory | memory node(s), base, size, reserved ranges | Address/size cell widths and decoded values |
| CPU | CPU nodes, compatible, release method, cache/topology hints | Every CPU node and relevant properties |
| Interrupts | interrupt-controller node, compatible, address, interrupt cells | Controller node and parent relationships |
| Timers | timer nodes, address, IRQ, clock references | DeviceTree properties |
| Clocks/resets | provider nodes and consumer references | Provider phandles and decoded links |
| GPIO | controller nodes, address, interrupt and pin properties | Node path and properties |
| UART | controller nodes, address, clock and interrupt | Candidate console and evidence |
| I2C/SPI | controller nodes and child devices | Bus addresses, IRQs and compatible strings |
| NAND/storage | controller, geometry hints, DMA/IRQ | DeviceTree plus firmware/kernel corroboration |
| Display | display engine, DSI, panel, framebuffer properties | Node path and display-specific values |
| Wireless | Wi-Fi and Bluetooth nodes, transport and IRQ | Node path and compatible strings |
| Baseband | modem node, transport and GPIO handshakes | Node path; keep optional for first boot |

For each recorded item include:
- IPSW filename and SHA-256;
- build version (9B206);
- DeviceTree archive path and extracted-container SHA-256;
- exact node path and property name;
- raw bytes and decoded value;
- decoding endianness and cell width;
- confidence: direct, corroborated, or inferred.

Apple's DeviceTree properties are untyped byte arrays. Do not assume that a four-byte property is a big-endian integer or a little-endian integer without checking the platform convention and corroborating it against kernel/firmware behavior.

## 4. Initial boot-chain inventory

The same IPSW should be used to record the N94-specific names and versions for:
- `LLB.n94ap.RELEASE.img3`;
- `iBSS.n94ap.RELEASE.dfu`;
- `iBEC.n94ap.RELEASE.dfu`;
- `iBoot.n94ap.RELEASE.img3`;
- `DeviceTree.n94ap.img3`;
- the N94 kernelcache.

These filenames are expected naming patterns, not proof that every file is present under that exact name in 9B206. Confirm each entry from the archive and BuildManifest. Do not implement the boot-ROM chain until the N94 entry state and handoff are understood.

## 5. M0 exit criteria

M0 is complete only when all of the following are checked in:
- [ ] IPSW checksum matches the selected 9B206 baseline.
- [ ] BuildManifest confirms the iPhone4,1 / n94ap build identity.
- [ ] N94 DeviceTree payload is located and its archive path recorded.
- [ ] Raw/decrypted DeviceTree is successfully parsed.
- [ ] Memory ranges and reserved regions are recorded.
- [ ] CPU topology and interrupt-controller nodes are recorded.
- [ ] Clock/reset, UART, GPIO, I2C and SPI nodes are inventoried.
- [ ] Every numeric value has a source node/property and byte-order explanation.
- [ ] No N90AP/A4 constants have been silently reused.

## 6. Current blockers

The GitHub worktree does not contain the 803 MiB IPSW or a decoded N94 DeviceTree. Therefore no N94 MMIO base, IRQ number, clock ID or memory base is asserted here yet. The next data input needed is the locally obtained 9B206 IPSW, or the raw N94 DeviceTree extracted from it.
