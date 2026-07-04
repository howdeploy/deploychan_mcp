---
id: flipper-zero
name: 'FlipperZero: agent-driven control'
summary: >-
  How an agent drives FlipperZero from a computer: via the UART Bridge — WiFi board,
  modules, and DIY devices over UART; with the Bridge off — the native CLI
  (install/remove apps, browse files). Three methods (native 230400 / Marauder
  115200 / pyflipper 9600), pitfalls, and serial access on NixOS.
type: tool
author: third_party
recommended: false
added: 2026-07-04
tags: [flipper, hardware, uart, cli, agent, nixos]
source: https://docs.flipper.net/zero/development/cli
---

# FlipperZero: agent-driven control

## What it is

FlipperZero is a compact hacker multitool for interacting with electronic systems: access
control, radio protocols, NFC, RFID, infrared devices. Inside — an STM32WB55
(Cortex-M4 + radio M0+), a 128×64 monochrome screen. In hardware it can do:

- **Sub-GHz** (CC1101, 315/433/868/915 MHz) — key fobs, barrier gates, IoT sensors.
- **NFC** 13.56 MHz (ISO14443A/B, Mifare) and **125 kHz RFID** (EM4100, HID, Indala…).
- **Infrared** receiver/transmitter — a universal remote.
- **GPIO** (13 pins, 3.3V) — UART/SPI/I2C/1-Wire for external modules.
- **iButton** (1-Wire), **Bluetooth LE**, **BadUSB** (HID emulation).

Out of the box — short range and no WiFi. From there it expands with modules: a **WiFi dev
board on ESP32-S2** (over UART), GPS, radio, and DIY builds. You need an SD card (16–32 GB is
enough; Kingston/Samsung/SanDisk).

## How an agent controls it — two modes

The key idea: the agent hooks into the Flipper over serial and works in one of two modes.

- **UART Bridge on** → the agent talks NOT to the Flipper itself, but to the module on the
  GPIO: the WiFi board (ESP32), any inserted module, or a DIY device. Everything hanging on
  the UART becomes available to the agent through the Flipper as a bridge.
- **UART Bridge off** → the agent works with the Flipper's own native CLI: manages apps
  (installs/removes `.fap`), browses the filesystem, pokes subsystems
  (Sub-GHz, NFC, GPIO, storage).

The Bridge blocks the native CLI — these are mutually exclusive modes (see pitfalls).

## Serial connection

The Flipper shows up as `/dev/ttyACM0`. The stable path is the symlink
`/dev/serial/by-id/usb-Flipper_Devices_Inc._*_flip_*-if00`.

| Method | Baud | Purpose |
|---|---|---|
| Native CLI | `230400` | Full control: Sub-GHz, NFC, RFID, IR, GPIO, Storage |
| Marauder UART Bridge | `115200` | WiFi attacks on the ESP32 dev board via USB-UART Bridge |
| pyflipper (Python) | `9600` | Scripted automation |

## Method 1 — native CLI (230400)

```bash
screen /dev/ttyACM0 230400
# or
picocom -b 230400 /dev/ttyACM0
```

| Command | Description |
|---|---|
| `help` | List all commands |
| `info device` | Device info (firmware, hardware, radio stack) |
| `subghz` | Sub-GHz radio (receive/transmit) |
| `nfc` | Read/emulate NFC |
| `rfid` | LF RFID |
| `ir` | Infrared port |
| `gpio` | GPIO pin control |
| `storage` | Filesystem operations |
| `loader list` | List installed `.fap` |
| `log` | System log |
| `power reboot` | Reboot the Flipper |

Exit screen: `Ctrl+A`, then `K`, then `Y`.

## Method 2 — Marauder CLI (115200)

Controlling the ESP32 WiFi dev board with Marauder firmware:

> **⚠️ Lawful use only.** `attack deauth`/`beacon`/`probe` and sniffing are active attacks on WiFi.
> Use them ONLY on networks you own yourself, or that you have written authorization to test
> (your own lab, an authorized pentest). Attacking networks that aren't yours is illegal.

1. On the Flipper: launch the **USB-UART Bridge** (`GPIO` → `USB-UART Bridge`).
2. Connect at the ESP32's baud rate:

```bash
screen /dev/ttyACM0 115200
```

| Command | Description |
|---|---|
| `help` | List Marauder commands |
| `scanap` | Scan WiFi access points |
| `listap` | Show discovered APs |
| `select <N>` | Select an AP by index |
| `attack deauth` | Deauth attack on the selected AP |
| `attack beacon` | Beacon spam |
| `attack probe` | Probe-request attack |
| `sniff` | Traffic sniffing |
| `stop` | Stop the attack |
| `status` | Device status |

## Method 3 — pyflipper (Python, 9600)

A library for programmatic control of the Flipper.

```bash
nix-shell -p python313Packages.pyflipper --run python3
```

```python
from pyflipper import PyFlipper
f = PyFlipper(com="/dev/ttyACM0")

print(f.device_info.info())              # info
f.subghz.tx("AB12CD", frequency=433920000, count=10)  # Sub-GHz TX
f.nfc.detect()                            # NFC
f.gpio.set("PA7", 1)                      # GPIO
f.storage.list("/ext")                    # files
f.led.set("blue", 255)                    # LED
```

Modules: `device_info`, `subghz`, `nfc`, `rfid`, `ir`, `gpio`, `storage`, `led`,
`vibro`, `bt`, `loader`, `power`, `update`, `log`, `date`, `music_player`, `ikey`,
`onewire`, `i2c`, `input`, `free`, `ps`, `debug`.

## Pitfalls

- **Don't mix up the baud rates:** CLI = 230400, Marauder = 115200, pyflipper = 9600.
- **The UART Bridge blocks the native CLI** — with the Bridge active, the direct CLI is unavailable.
- **qFlipper holds the port** — close qFlipper before `screen`/`picocom`/`pyflipper`.
- **Before serial work, kill background processes on the port:**
  ```bash
  for pid in $(lsof -t /dev/ttyACM0 2>/dev/null); do kill -9 $pid 2>/dev/null; done
  ```
- **pyflipper hardcodes 9600** — it doesn't work with some custom firmwares; fall back to the native CLI (screen 230400).
- **CHIP_TUNE (Momentum firmware)** — an isolated image format, NOT real Mass Storage; files written there are invisible to apps. For actual file transfer use the CLI `storage write`, not mounting CHIP_TUNE.
- **`storage write` can corrupt binaries** — for firmware and binary transfer use the qFlipper file manager.
- **`.fzt` (Flizzer Tracker) — do NOT use:** the `flizzer_tracker` app instantly crashes the Flipper on playback.
- **Managing apps:** never remove apps without an explicit command from a human. Even if an app looks like "obvious junk" — describe it first, then ask for confirmation.

## Serial access on NixOS

The Flipper is USB VID:PID `0483:5740`, `MODE="0660"` + `GROUP="dialout"` by default.

**Option A — user in the dialout group (simplest):**
```nix
users.users.YOUR_USER.extraGroups = [ "dialout" ];
```
Requires re-login (groups are assigned at login).

**Option B — udev rule (no session restart):**
```nix
services.udev.extraRules = ''
  SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666"
  SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666", GROUP="dialout"
'';
```

Why TWO rules: **tty** — for the serial CLI (`screen`/`picocom`/`pyflipper` via
`/dev/ttyACM0`); **usb** — for GUI tools like **qFlipper** that open USB directly through
libusb. Without the usb rule, qFlipper will loop on `Access denied`.

**CRITICAL: use `:=`, not `=`.** System rules set `MODE="0660"`; a plain `MODE="0666"` gets
overridden by the default rules. `:=` is a final assignment — nothing can override it after that.

Apply to an already plugged-in device:
```bash
sudo chmod 666 /dev/ttyACM0
sudo udevadm trigger --action=add --attr-match=idVendor=0483 --attr-match=idProduct=5740
ls -la /dev/ttyACM0   # should be crw-rw-rw- (0666)
```
Pitfall: `udevadm trigger` WITHOUT `--action=add` doesn't recreate the node — the old permissions stay.

Tools in systemPackages: `screen`, `picocom`, `qflipper` (pyflipper — via
`nix-shell -p python313Packages.pyflipper`).
