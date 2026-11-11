# iPhone 4S (n94ap, S5L8940 "A5"): `-M iPhone-4S` (planned)

Status: planning. No board, SoC model or machine type exists in the tree yet. This document collects
what the board needs; each claim is marked as verified, or as a to-do where it still needs checking
against the IPSW, the device tree or real hardware.

The A5 is a different SoC from the A4 (`../n90/README.md`, `../n81/README.md`, `../ipad1/README.md`).
Expect a new `hw/arm/s5l8940*.c` set, not a new `A4Board` entry. The A4 peripherals (`s5l8930_*.c`) are
the reuse candidates to measure, not assumptions.

## Identity

| Field | Value | Status |
|---|---|---|
| Model identifier | iPhone4,1 | verified by iPhone4,1 device metadata; confirm again in selected BuildManifest |
| Board config | n94ap | verified by device metadata and N94 firmware naming; confirm in selected BuildManifest |
| Marketing name | iPhone 4S | known |
| SoC | Apple S5L8940 "A5" | CPID 0x8940 and platform s5l8940x verified by device metadata; DT corroboration pending |
| CPU | dual-core ARM Cortex-A9 (ARMv7-A, MPCore) | known; the A4 is a single-core Cortex-A8 |
| GPU | PowerVR SGX543MP2 | known; the A4 has an SGX535 |
| DRAM | 512 MiB | known; to verify in the IPSW DT |
| Panel | 3.5" 960x640 Retina, portrait | known; panel ID to verify |
| Digitizer | multi-touch, portrait | to verify (driver and firmware) |
| Camera | 8 MP rear, VGA front | known; sensor models to verify |
| Wi-Fi | Broadcom BCM4330 | teardown identifies the chip; driver/firmware behavior still needs DT verification |
| Baseband | modem with GSM/CDMA; part to verify | to verify |
| Sensors | accelerometer, gyro, proximity/ambient light, compass | to verify (I2C addresses from the DT) |
| Storage | NAND, 8/16/32/64 GB variants | to verify per variant |

## Firmware targets

| Build | iOS | Notes | Status |
|---|---|---|---|
| 9A334 | 5.0 | first iOS for the device | to verify (IPSW, keys) |
| 9B176 | 5.0.1 | | to verify |
| 9B206 | 5.1.1 | selected M0 baseline; IPSW identity/checksums in m0-device-tree.md | metadata verified; raw DeviceTree pending |
| 9 series, later | 6.x, 7.x, 8.x, 9.x | out of scope until 5.1.1 boots | not started |

Plan: start with 9B206. Record the IPSW SHA-1 and the source (archive.org or Apple's CDN) here once
fetched. Firmware and images stay in `~/Developer/qemu-ios-files/n94/`, never in the repository.

## Boot chain

To verify on the IPSW:

- iBoot / LLB and their versions for 9B206
- whether the kernelcache and the DeviceTree use the same layout as the A4 (`iPhone3,1`)
- the boot ROM entry and the SRAM / DFU path, which the A4 boards reach through the same code

## Board plan

Ordered, each step is checkable:

1. Extract from the IPSW: device tree (ChipID, board-id, memory map, IRQ numbers, I2C and SPI nodes,
   GPIO list) and the baseband node. Record each value in this file with its source.
2. Write the SoC skeleton: the Cortex-A9 MPCore (two CPUs, GIC), the timer and the memory map. The
   new file set is `hw/arm/s5l8940*.c` and `include/hw/arm/s5l8940*.h`.
3. Measure the reuse of `s5l8930_*.c`: which blocks have the same register layout (GPIO, I2C, SPI,
   DART, PMU, display, SDIO, H2FMI). Write the result as a table: reuse, adapt, new.
4. Add the `iPhone-4S` machine type with a board struct, in a new file (not `ipad1.c`, which is A4).
5. Boot to the boot ROM / iBoot stage. Gate: serial output reaches the iBoot banner.
6. Boot to the kernel. Gate: kernel console on the serial log.

## Reuse candidates from the A4 tree

These come from `hw/arm/`, unverified for the A5:

- `s5l8930_gpio.c`, `s5l8930_i2c.c`, `s5l8930_i2s.c`, `s5l8930_sdio.c`
- `s5l8930_dart.c` (IOMMU), `s5l8930_pmgr.c` (power), `s5l8930_dmc.c` (memory controller)
- `s5l8930_h2fmi.c` (NAND), `s5l8930_sha1.c`
- `s5l8930_display.c`, `s5l8930_isp.c` (camera), `s5l8930_iop*.c` (IOP mailbox)
- `s5l8920_pwm.c` (PWM, the vibrator), `s5l8920_jpeg.c`

Anything not on this list is new work or unknown.

## Open questions

- Is the GPU path the same host GL bridge (`hw/arm/gles-host*.c`) with a new SGX543 contract, or new work?
- Which baseband model applies, and does the modem need the cell stream the n90 board waits on?
- How is the BCM4330 Wi-Fi/Bluetooth silicon wired and initialized on N94AP? Do not assume the N90 BCM4329 personality applies.
- Which target is the right one for the GL work: 5.1.1 first, or the 4.x line first?

## M0 evidence workflow

The first evidence-collection milestone is tracked in [m0-device-tree.md](m0-device-tree.md). The IPSW inventory helper is [tools/n94/inspect_ipsw.py](../../tools/n94/inspect_ipsw.py). No N94 memory or MMIO constants should be added until that workflow produces a decoded tree and source-backed register inventory.

## Sources

To add with each fact: the IPSW name and SHA-1, the BuildManifest entry, and the device tree
node path. Do not cite a forum or a wiki as the source for a value without checking it against
the IPSW.

## Correct SoC naming

For N94AP, use **S5L8940 / A5** for the application processor and **s5l8940x** for the firmware platform string. The device metadata identifies CPID 0x8940 and BDID 0x08. Do not call this chip S5L8942: S5L8942 is the A5 Rev A variant used in other products, not the iPhone 4S. The similarly named platform string s5l8940x is not itself the silicon part number.

Useful cross-checks:
- [IPSW.me iPhone4,1 device metadata](https://ipsw.me/iPhone4%2C1/info/) lists board n94ap, platform s5l8940x, BDID 0x08 and CPID 0x8940.
- [The iPhone Wiki: Application Processor](https://www.theiphonewiki.com/wiki/Application_Processor) lists S5L8940 A5 for iPhone 4S and S5L8942 A5 Rev A for different products.
- [The iPhone Wiki: A5 variants](https://www.theiphonewiki.com/wiki/A5) distinguishes S5L8940 from S5L8942.
- [iFixit iPhone 4S teardown](https://documents.cdn.ifixit.com/pdf/ifixit/guide_6610_en.pdf) identifies the Apple A5 dual-core processor and lists the BCM4330 wireless chip.

## Hardware facts and cautions

| Item | Current finding | Emulator consequence |
|---|---|---|
| CPU | Dual-core ARM Cortex-A9, ARMv7-A | Model the A5 CPU cluster and secondary-core startup; the A4 single Cortex-A8 path is not equivalent |
| RAM | 512 MiB | Verify exact physical base and reservations from the N94 device tree before mapping |
| GPU | PowerVR SGX543MP2 | Do not assume the A4 SGX535/graphics path is binary-compatible |
| Wi-Fi | BCM4330 identified in teardown references | Do not reuse the repo's BCM4329 board personality without evidence |
| Cellular | iPhone 4S has GSM/CDMA-capable variants and a separate modem path | Treat modem model and board wiring as a separate research item |
| Storage | NAND-based device; capacities vary by product configuration | Determine controller, geometry and FTL behavior from the target firmware/device tree |

The table distinguishes product-level hardware identification from the details needed to emulate it. Register addresses, IRQs, clock IDs, panel IDs and peripheral protocols remain unknown until recorded from N94-specific evidence.

## Current evidence rule

For every value added to the implementation, record one of:
1. direct N94 device-tree property;
2. firmware/boot-stage trace with build identifier;
3. hardware observation with method and conditions;
4. a clearly labeled inference with its supporting evidence.

A value copied from N90AP is not N94 evidence. A matching device-tree compatible string is a reuse candidate, not proof of identical register semantics.
