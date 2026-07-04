---
id: flipper-zero
name: 'FlipperZero: управление агентом'
summary: >-
  Как агент управляет FlipperZero с компьютера: через UART Bridge — WiFi-плата,
  модули и самодельные устройства по UART; с выключенным Bridge — нативный CLI
  (ставить/удалять апки, смотреть файлы). Три метода (native 230400 / Marauder
  115200 / pyflipper 9600), подводные камни и доступ к serial на NixOS.
type: tool
author: third_party
recommended: false
added: 2026-07-04
tags: [flipper, hardware, uart, cli, agent, nixos]
source: https://docs.flipper.net/zero/development/cli
---

# FlipperZero: управление агентом

## Что это

FlipperZero — компактный хакерский мультитул для взаимодействия с электронными
системами: контроль доступа, радиопротоколы, NFC, RFID, инфракрасные устройства.
Внутри — STM32WB55 (Cortex-M4 + радио-M0+), монохромный экран 128×64. Аппаратно умеет:

- **Sub-GHz** (CC1101, 315/433/868/915 МГц) — брелоки, шлагбаумы, IoT-датчики.
- **NFC** 13.56 МГц (ISO14443A/B, Mifare) и **125 кГц RFID** (EM4100, HID, Indala…).
- **Инфракрасный** приёмник/передатчик — универсальный пульт.
- **GPIO** (13 пинов, 3.3V) — UART/SPI/I2C/1-Wire для внешних модулей.
- **iButton** (1-Wire), **Bluetooth LE**, **BadUSB** (эмуляция HID).

Из коробки — малая дальность и нет WiFi. Дальше расширяется модулями: **WiFi-девборд
на ESP32-S2** (по UART), GPS, радио и самоделки. Нужна SD-карта (16–32 ГБ хватит;
Kingston/Samsung/SanDisk).

## Как агент им управляет — два режима

Ключевая идея: агент цепляется к Flipper по serial и работает в одном из двух режимов.

- **UART Bridge включён** → агент говорит НЕ с самим Flipper, а с модулем на GPIO:
  WiFi-платой (ESP32), любым вставленным модулем или самодельным устройством. Всё, что
  висит на UART, становится доступно агенту через Flipper как мост.
- **UART Bridge выключен** → агент работает с нативным CLI самого Flipper: управляет
  приложениями (ставит/удаляет `.fap`), смотрит файловую систему, дёргает подсистемы
  (Sub-GHz, NFC, GPIO, storage).

Bridge блокирует нативный CLI — это взаимоисключающие режимы (см. подводные камни).

## Serial-подключение

Flipper появляется как `/dev/ttyACM0`. Стабильный путь — симлинк
`/dev/serial/by-id/usb-Flipper_Devices_Inc._*_flip_*-if00`.

| Метод | Baud | Для чего |
|---|---|---|
| Нативный CLI | `230400` | Полный контроль: Sub-GHz, NFC, RFID, IR, GPIO, Storage |
| Marauder UART Bridge | `115200` | WiFi-атаки на ESP32-девборде через USB-UART Bridge |
| pyflipper (Python) | `9600` | Скриптовая автоматизация |

## Метод 1 — нативный CLI (230400)

```bash
screen /dev/ttyACM0 230400
# или
picocom -b 230400 /dev/ttyACM0
```

| Команда | Описание |
|---|---|
| `help` | Список всех команд |
| `info device` | Инфо об устройстве (прошивка, железо, радио-стек) |
| `subghz` | Sub-GHz радио (приём/передача) |
| `nfc` | Чтение/эмуляция NFC |
| `rfid` | LF RFID |
| `ir` | Инфракрасный порт |
| `gpio` | Управление пинами GPIO |
| `storage` | Операции с файловой системой |
| `loader list` | Список установленных `.fap` |
| `log` | Системный лог |
| `power reboot` | Ребут Flipper |

Выход из screen: `Ctrl+A`, затем `K`, затем `Y`.

## Метод 2 — Marauder CLI (115200)

Управление ESP32 WiFi-девбордом с прошивкой Marauder:

1. На Flipper: запусти **USB-UART Bridge** (`GPIO` → `USB-UART Bridge`).
2. Подключись на скорости ESP32:

```bash
screen /dev/ttyACM0 115200
```

| Команда | Описание |
|---|---|
| `help` | Список команд Marauder |
| `scanap` | Скан точек доступа WiFi |
| `listap` | Показать найденные AP |
| `select <N>` | Выбрать AP по индексу |
| `attack deauth` | Deauth-атака на выбранную AP |
| `attack beacon` | Beacon spam |
| `attack probe` | Probe-request атака |
| `sniff` | Снифинг трафика |
| `stop` | Остановить атаку |
| `status` | Статус устройства |

## Метод 3 — pyflipper (Python, 9600)

Библиотека для программного контроля Flipper.

```bash
nix-shell -p python313Packages.pyflipper --run python3
```

```python
from pyflipper import PyFlipper
f = PyFlipper(com="/dev/ttyACM0")

print(f.device_info.info())              # инфо
f.subghz.tx("AB12CD", frequency=433920000, count=10)  # Sub-GHz TX
f.nfc.detect()                            # NFC
f.gpio.set("PA7", 1)                      # GPIO
f.storage.list("/ext")                    # файлы
f.led.set("blue", 255)                    # LED
```

Модули: `device_info`, `subghz`, `nfc`, `rfid`, `ir`, `gpio`, `storage`, `led`,
`vibro`, `bt`, `loader`, `power`, `update`, `log`, `date`, `music_player`, `ikey`,
`onewire`, `i2c`, `input`, `free`, `ps`, `debug`.

## Подводные камни

- **Не путай baud:** CLI = 230400, Marauder = 115200, pyflipper = 9600.
- **UART Bridge блокирует нативный CLI** — при активном Bridge прямой CLI недоступен.
- **qFlipper занимает порт** — закрой qFlipper перед `screen`/`picocom`/`pyflipper`.
- **Перед serial-работой убей фоновые процессы на порту:**
  ```bash
  for pid in $(lsof -t /dev/ttyACM0 2>/dev/null); do kill -9 $pid 2>/dev/null; done
  ```
- **pyflipper хардкодит 9600** — с некоторыми кастом-прошивками не работает; откатывайся на нативный CLI (screen 230400).
- **CHIP_TUNE (Momentum firmware)** — изолированный формат образа, НЕ реальный Mass Storage; записанные туда файлы невидимы приложениям. Для реального переноса — CLI `storage write`, не монтирование CHIP_TUNE.
- **`storage write` может портить бинарники** — для прошивок и бинарного переноса используй файловый менеджер qFlipper.
- **`.fzt` (Flizzer Tracker) — НЕ использовать:** приложение `flizzer_tracker` мгновенно крашит Flipper при воспроизведении.
- **Управление приложениями:** никогда не удаляй апки без явной команды человека. Даже если апка выглядит «очевидным мусором» — сначала опиши её, потом спрашивай подтверждение.

## Доступ к serial на NixOS

Flipper — это USB VID:PID `0483:5740`, `MODE="0660"` + `GROUP="dialout"` по умолчанию.

**Вариант A — пользователь в группе dialout (проще всего):**
```nix
users.users.YOUR_USER.extraGroups = [ "dialout" ];
```
Нужен релогин (группы назначаются при входе).

**Вариант B — udev-правило (без перезапуска сессии):**
```nix
services.udev.extraRules = ''
  SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666"
  SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666", GROUP="dialout"
'';
```

Зачем ДВА правила: **tty** — для serial-CLI (`screen`/`picocom`/`pyflipper` через
`/dev/ttyACM0`); **usb** — для GUI-тулз вроде **qFlipper**, которые открывают USB напрямую
через libusb. Без usb-правила qFlipper зациклится на `Access denied`.

**КРИТИЧНО: используй `:=`, а не `=`.** Системные правила ставят `MODE="0660"`; простое
`MODE="0666"` перекрывается дефолтными правилами. `:=` — финальное присваивание, его уже
никто не переопределит.

Применить к уже воткнутому устройству:
```bash
sudo chmod 666 /dev/ttyACM0
sudo udevadm trigger --action=add --attr-match=idVendor=0483 --attr-match=idProduct=5740
ls -la /dev/ttyACM0   # должно быть crw-rw-rw- (0666)
```
Подводный камень: `udevadm trigger` БЕЗ `--action=add` не пересоздаёт узел — старые права остаются.

Инструменты в systemPackages: `screen`, `picocom`, `qflipper` (pyflipper — через
`nix-shell -p python313Packages.pyflipper`).
