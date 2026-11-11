# N94AP hardware research log

This file records evidence and open questions for the iPhone 4S (iPhone4,1 / N94AP). Update it from actual firmware/device-tree inspection and reproducible traces. Do not fill unknown fields by copying values from N90AP.

## Identity cross-check

| Field | Value |
|---|---|
| Product type | iPhone4,1 |
| Board | n94ap |
| Chip family | S5L8940 / A5 (firmware platform: s5l8940x) |
| Chip ID | 0x8940 |
| Board ID | 0x08 |
| Screen | 640 × 960 |

References:
- ios-deploy device database: https://github.com/ios-control/ios-deploy/blob/master/src/ios-deploy/device_db.h
- UFADE device table: https://github.com/prosch88/UFADE/blob/main/ufade/irecv_devices.py
- MagicCFG device table: https://github.com/j4nf4b3l/MagicCFG-Reloaded/blob/main/ircv.c
- Device inventory: https://github.com/sferrini/iosdevices

## Evidence ledger

| Topic | Evidence currently available | Confidence | Next action |
|---|---|---|---|
| Board identity | IPSW device metadata maps iPhone4,1 to n94ap, platform s5l8940x, BDID 0x08 and CPID 0x8940 | High | Preserve the metadata source and confirm against the selected BuildManifest |
| SoC family | CPID 0x8940 / A5; platform string s5l8940x | High for identity | Verify N94-specific compatible strings and CPU topology in the decoded DeviceTree |
| CPU topology | A5 platform is dual-core ARM Cortex-A9 | High | Verify QEMU CPU model, reset and secondary-core release from boot traces |
| DRAM layout | No N94-specific map recorded in this repository | Unknown | Extract memory map from device tree and boot arguments |
| Interrupt controller | No N94-specific map recorded | Unknown | Inventory interrupt-controller nodes and parent relationships |
| Clock / power manager | No N94-specific register map recorded | Unknown | Inventory clock/reset providers and first-stage accesses |
| Display / touch | Only product-level display dimensions known here | Partial | Inspect panel, DSI and digitizer nodes |
| NAND / storage | No N94-specific controller model selected | Unknown | Inspect storage nodes, geometry and firmware expectations |
| Connectivity | BCM4330 identified by teardown; N94 transport nodes not inspected | Partial | Inventory Wi-Fi, Bluetooth and baseband nodes in the decoded DeviceTree |

## Selected firmware baseline

| Field | Value |
|---|---|
| IPSW | iPhone4,1_5.1.1_9B206_Restore.ipsw |
| Product version / build | 5.1.1 / 9B206 |
| SHA-1 | ac99928cc52fcb24502959ace3c36a63ba75ab6c |
| SHA-256 | b6870acf127a58e2775f93b9314cc678ac39caed7f0cbd13699f5f3a09c6f277 |
| Published size | 803 MiB |
| DeviceTree payload name | DeviceTree.n94ap.img3 |
| Raw DeviceTree parsed in this worktree | No |

Source: [IPSW Downloads 9B206 metadata](https://ipsw.me/download/iPhone4,1/9B206/) and [iPhone4,1 device metadata](https://ipsw.me/iPhone4,1/info/). The DeviceTree is an Apple-specific binary tree packaged in an IMG3/IM4P container; the wrapper may be encrypted. See [The Apple Wiki DeviceTree format notes](https://theapplewiki.com/wiki/DeviceTree).

## Device-tree capture template

For each relevant N94AP node, record:
- Node path and compatible string.
- reg ranges, including address and size cells.
- Interrupt parent and interrupt specifier.
- Clock, reset, GPIO, DMA and power-domain references.
- Firmware build and source path.
- Whether the value is directly present in the device tree or inferred from a trace.
- A short note explaining confidence and ambiguity.

Do not publish firmware binaries, private signing material or extracted proprietary assets in this repository. Keep only the minimum factual metadata needed to explain the model.

## Register-map template

| Block | Base | Size | IRQs | Evidence | Model status |
|---|---:|---:|---|---|---|
| CPU / interrupt controller | TBD | TBD | TBD | TBD | Not modeled |
| Clock / power manager | TBD | TBD | TBD | TBD | Not modeled |
| GPIO | TBD | TBD | TBD | TBD | Not modeled |
| UART | TBD | TBD | TBD | TBD | Not modeled |
| I2C / SPI | TBD | TBD | TBD | TBD | Not modeled |
| NAND controller | TBD | TBD | TBD | TBD | Not modeled |
| Display controller | TBD | TBD | TBD | TBD | Not modeled |

## Important A4 comparison

N90AP is an A4/S5L8930 board. Its constants in include/hw/arm/s5l8930.h and hw/arm/ipad1.c are useful only as comparison points. A matching peripheral name or similar device-tree property does not prove that the A5 block has the same register layout, timing, interrupt routing or reset behavior.

Any shared model must be justified at the individual IP-block level and covered by tests.

## M0 execution status

- [x] Select iPhone4,1 / n94ap as the board identity.
- [x] Select iOS 5.1.1 build 9B206 as the first firmware baseline and record published checksums.
- [x] Add an IPSW BuildManifest/DeviceTree inventory helper and synthetic archive tests.
- [ ] Run the helper against the actual local 9B206 IPSW.
- [ ] Extract/decrypt and parse the raw N94 DeviceTree.
- [ ] Record memory, CPU, interrupt, clock, UART, GPIO, I2C and SPI properties with source paths.

The first three items are repository work. The remaining items require the actual IPSW payload; no hardware addresses are guessed to fill the gap.

## Variant distinction

N94AP / iPhone4,1 uses the original S5L8940 A5 (CPID 0x8940, platform string s5l8940x). S5L8942 is the A5 Rev A variant used in other products; it is not the iPhone 4S application processor. Sources: [IPSW.me device metadata](https://ipsw.me/iPhone4%2C1/info/), [The iPhone Wiki application processor list](https://www.theiphonewiki.com/wiki/Application_Processor), and [A5 variant overview](https://www.theiphonewiki.com/wiki/A5).

## Wireless silicon note

The iPhone 4S teardown identifies Broadcom BCM4330 wireless silicon. The BCM4329 model already present in this repository must not be selected as the N94 Wi-Fi personality without evidence. Keep the exact driver firmware, SDIO wiring, interrupt and Bluetooth integration as unresolved until confirmed from the N94 device tree and firmware.
