# iPhone 4S (n94ap, S5L8942 "A5"): `-M iPhone-4S` (planned)

Status: planning. No board, SoC model or machine type exists in the tree yet. This document collects
what the board needs; each claim is marked as verified, or as a to-do where it still needs checking
against the IPSW, the device tree or real hardware.

The A5 is a different SoC from the A4 (`../n90/README.md`, `../n81/README.md`, `../ipad1/README.md`).
Expect a new `hw/arm/s5l8942*.c` set, not a new `A4Board` entry. The A4 peripherals (`s5l8930_*.c`) are
the reuse candidates to measure, not assumptions.

## Identity

| Field | Value | Status |
|---|---|---|
| Model identifier | iPhone4,1 | to verify (IPSW BuildManifest / Restore.plist) |
| Board config | n94ap | to verify |
| Marketing name | iPhone 4S | known |
| SoC | Apple S5L8942 "A5" | to verify (ChipID in the device tree) |
| CPU | dual-core ARM Cortex-A9 (ARMv7-A, MPCore) | known; the A4 is a single-core Cortex-A8 |
| GPU | PowerVR SGX543MP2 | known; the A4 has an SGX535 |
| DRAM | 512 MiB | known; to verify in the IPSW DT |
| Panel | 3.5" 960x640 Retina, portrait | known; panel ID to verify |
| Digitizer | multi-touch, portrait | to verify (driver and firmware) |
| Camera | 8 MP rear, VGA front | known; sensor models to verify |
| Wi-Fi | Broadcom BCM4751 (Wi-Fi + Bluetooth) | to verify; the BCM4329 model in the repo is not this part |
| Baseband | modem with GSM/CDMA; part to verify | to verify |
| Sensors | accelerometer, gyro, proximity/ambient light, compass | to verify (I2C addresses from the DT) |
| Storage | NAND, 8/16/32/64 GB variants | to verify per variant |

## Firmware targets

| Build | iOS | Notes | Status |
|---|---|---|---|
| 9A334 | 5.0 | first iOS for the device | to verify (IPSW, keys) |
| 9B176 | 5.0.1 | | to verify |
| 9B206 | 5.1.1 | the first target: same build the n90 work used | to verify (IPSW, keys) |
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
   new file set is `hw/arm/s5l8942*.c` and `include/hw/arm/s5l8942*.h`.
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
- Which Wi-Fi/Bluetooth chip model applies to the BCM4751 (not the BCM4329 model)?
- Which target is the right one for the GL work: 5.1.1 first, or the 4.x line first?

## Sources

To add with each fact: the IPSW name and SHA-1, the BuildManifest entry, and the device tree
node path. Do not cite a forum or a wiki as the source for a value without checking it against
the IPSW.