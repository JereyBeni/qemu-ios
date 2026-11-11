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
| Board identity | Multiple device tables map iPhone4,1 to n94ap | High | Preserve references with future changes |
| SoC family | Device tables map n94ap to CPID 0x8940 / S5L8940; platform string is s5l8940x | High | Verify compatible strings in N94 device tree |
| CPU topology | A5 platform is dual-core ARM Cortex-A9 | High | Verify QEMU CPU model, reset and secondary-core release from boot traces |
| DRAM layout | No N94-specific map recorded in this repository | Unknown | Extract memory map from device tree and boot arguments |
| Interrupt controller | No N94-specific map recorded | Unknown | Inventory interrupt-controller nodes and parent relationships |
| Clock / power manager | No N94-specific register map recorded | Unknown | Inventory clock/reset providers and first-stage accesses |
| Display / touch | Only product-level display dimensions known here | Partial | Inspect panel, DSI and digitizer nodes |
| NAND / storage | No N94-specific controller model selected | Unknown | Inspect storage nodes, geometry and firmware expectations |
| Connectivity | No N94-specific transport map recorded | Unknown | Inventory Wi-Fi, Bluetooth and baseband nodes |

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

## Variant distinction

N94AP / iPhone4,1 uses the original S5L8940 A5 (CPID 0x8940, platform string s5l8940x). S5L8942 is the A5 Rev A variant used in other products; it is not the iPhone 4S application processor. Sources: [IPSW.me device metadata](https://ipsw.me/iPhone4%2C1/info/), [The iPhone Wiki application processor list](https://www.theiphonewiki.com/wiki/Application_Processor), and [A5 variant overview](https://www.theiphonewiki.com/wiki/A5).

## Wireless silicon note

The iPhone 4S teardown identifies Broadcom BCM4330 wireless silicon. The BCM4329 model already present in this repository must not be selected as the N94 Wi-Fi personality without evidence. Keep the exact driver firmware, SDIO wiring, interrupt and Bluetooth integration as unresolved until confirmed from the N94 device tree and firmware.
