---
id: nixos-administration
name: 'NixOS: администрирование системы'
summary: >-
  Практический гайд по администрированию NixOS: декларативный config-workflow и
  rebuild, nix-ld для непропатченных бинарников, LD_LIBRARY_PATH для Python ctypes,
  desktop-стек (waybar/niri/fuzzel/dunst/swayosd/GTK), EFI, serial, монтаж HDD,
  скриншоты, fastfetch и NOPASSWD-rebuild для автономного агента.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, administration, nix-ld, waybar, niri, desktop]
source: https://mcp.deploychan.webcam/docs
---

# Администрирование NixOS

Всё декларативно: система собирается из конфига, а не правится «на живую». Ниже —
рабочий цикл правки, nix-ld, интеграция с рабочим столом и NixOS-специфичные тонкости.

> **Обязательное vs вкус.** Для агента ОБЯЗАТЕЛЬНОЕ — цикл правки/rebuild, nix-ld,
> `LD_LIBRARY_PATH`, права на serial, EFI, монтаж HDD, автономный rebuild. Всё про
> ОФОРМЛЕНИЕ (Waybar, Niri, Fuzzel, Dunst, SwayOSD, GTK, обои, Fastfetch) — это ЛИЧНЫЙ
> вкус KISA (Catppuccin Mocha), помечено «вкус · пример». Это НЕ инструкция агенту, а
> пример «как можно». Агент повторяет вкус СВОЕГО пользователя, а не копирует этот.

## Базовый цикл: правка системного конфига

### 1. Прочитать текущий конфиг
```bash
cat /etc/nixos/configuration.nix
```

### 2. Применить изменения (точечная правка)
```bash
# Скопировать во temp (patch-инструмент может отказать на /etc/nixos/*)
sudo cp /etc/nixos/configuration.nix /tmp/configuration.nix
sudo chmod 666 /tmp/configuration.nix
# ... правишь /tmp/configuration.nix ...
sudo cp /tmp/configuration.nix /etc/nixos/configuration.nix
```

### 3. Проверить и пересобрать
```bash
sudo nixos-rebuild dry-build   # собрать конфиг БЕЗ применения — ловит ошибки заранее
sudo nixos-rebuild switch      # применить
```
После switch убедись, что нужные сервисы поднялись:
```bash
systemctl status <service>            # системный сервис
systemctl --user status <service>     # пользовательский (напр. waybar, hermes-gateway)
```

### Альтернатива: flake-система
```bash
cd /etc/nixos
sudo nix flake update
sudo nixos-rebuild switch --flake .#YOUR_HOSTNAME
```

## nix-ld: разделяемые библиотеки для непропатченных бинарников

NixOS не кладёт библиотеки в `/usr/lib/`. Непропатченные бинарники (Electron-приложения,
готовые CLI-тулзы, проприетарный софт) падают с `cannot open shared object file`.

### Включить
```nix
programs.nix-ld.enable = true;
```

### Добавить недостающие библиотеки
```nix
programs.nix-ld.libraries = with pkgs; [
    glib gtk3 nspr nss cups dbus at-spi2-core
    cairo pango gdk-pixbuf libdrm libxkbcommon
    libxshmfence libpulseaudio libgbm expat wayland
    zlib libpng libjpeg libwebp
    xorg.libxcb xorg.libXcomposite xorg.libXdamage
];
```

### Найти путь к библиотеке пакета
```bash
nix eval --raw nixpkgs#glib.outPath
# Избегай пакетов на '-bin' — у них нет /lib
```

## Разделяемые библиотеки для Python ctypes

Python-пакеты, использующие `ctypes.util.find_library` (например `sounddevice`), не
находят библиотеки на NixOS — даже когда те установлены.

### Фикс: добавить LD_LIBRARY_PATH
```nix
environment.sessionVariables.LD_LIBRARY_PATH = "/run/current-system/sw/lib";
```

## Рабочий стол — личный вкус (пример, не инструкция)

Разделы отсюда и до «Порядок загрузки EFI» (Waybar, Niri, Fuzzel, Dunst, SwayOSD, GTK,
обои), а также Fastfetch ниже — это ОФОРМЛЕНИЕ под вкус KISA (Catppuccin Mocha). Пример
«как можно», НЕ требование к агенту. Агент повторяет вкус СВОЕГО пользователя.

## Waybar на NixOS (вкус · пример)

### Включить
```nix
programs.waybar.enable = true;
```

Файлы конфига:
- `~/.config/waybar/config` — JSONC, раскладка модулей
- `~/.config/waybar/style.css` — CSS-стилизация

### Nerd Fonts
```nix
fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
];
```

### Pill-раскладка (Catppuccin Mocha)
Прозрачный бар, каждый модуль — отдельная «пилюля» с рамкой:

```css
window#waybar { background: transparent; }
#workspaces {
    background: #1E1E2E;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 0 8px;
    margin: 4px 12px 4px 0;
}
#clock {
    background: #1E1E2E;
    border: 1px solid #45475A;
    border-radius: 10px;
    padding: 0 20px;
    margin: 4px 0;
    font-weight: 700;
}
#cpu, #memory, #pulseaudio, #backlight, #battery, #network {
    background: #1E1E2E;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 0 10px;
    margin: 4px 1px;
}
```

### Формат часов (зависит от версии!)
| Версия Waybar | Формат |
|---|---|
| ≤ 0.9.x | `"%H:%M"` |
| ≥ 0.11 | `"{0:%H:%M}"` — обязателен позиционный `0:` |

### Иконка памяти
Используй `` (nf-oct-memory, U+E266) — Octicons, самая стабильная между версиями Nerd Fonts.

### wpctl volume — ВСЕГДА ограничивай
```bash
wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+
```

### Hover-эффекты (тонкие, без 3D/инверсии)
```css
#workspaces button { transition: none; }
#workspaces button:not(.active):hover {
    background: #313244; color: #A6ADC8; box-shadow: none;
}
#workspaces button.active:hover {
    background: #b89ae8; color: #1E1E2E; box-shadow: none;
}
```

### Стилизация тултипа
```css
tooltip {
    background: rgba(30, 30, 46, 0.94);
    border: 1px solid #CBA6F7;
    border-radius: 10px;
    padding: 8px 12px;
}
```

## Focus ring в Niri

```kdl
layout {
    focus-ring {
        width 2
        active-color "#CBA6F7"     # Mauve
        inactive-color "#313244"   # Surface0
    }
}
```

**Используй `layout { focus-ring { ... } }`, а НЕ `borders { ... }`** — старый синтаксис
приводит к тихому отклонению конфига.

## Лаунчер Fuzzel

Конфиг: `~/.config/fuzzel/fuzzel.ini`

```ini
[main]
font=JetBrains Mono Nerd Font:size=14
width=40
lines=12
border-radius=10
border-width=2

[colors]
background=1E1E2Eff
text=CDD6F4ff
match=CBA6F7ff
selection=CBA6F7ff
selection-text=1E1E2Eff
border=CBA6F7ff
```

**ЛОВУШКА:** `launch-prefix=app` тихо ломает запуск приложений. Убери его.

## Демон уведомлений Dunst

```ini
[global]
    font = JetBrains Mono Nerd Font 10
    geometry = "250x5-12-36"
    padding = 6
    horizontal_padding = 8
    max_icon_size = 24
    mouse_left_click = close_current
```

Установка: `nix profile install nixpkgs#dunst` или добавить в `environment.systemPackages`.

## SwayOSD — OSD громкости/яркости

```nix
environment.systemPackages = with pkgs; [ swayosd ];
```

Автозапуск в niri: `spawn-at-startup "swayosd-server"`

Интеграция в waybar (вместо сырого wpctl):
```json
"pulseaudio": {
    "on-click": "swayosd-client --output-volume mute-toggle",
    "on-scroll-up": "swayosd-client --output-volume raise",
    "on-scroll-down": "swayosd-client --output-volume lower"
}
```

**ЛОВУШКА:** `swayosd-client` недоступен до `nixos-rebuild switch`.

## GTK-темизация (без home-manager)

```nix
environment.systemPackages = with pkgs; [
    (catppuccin-gtk.override {
        variant = "mocha";
        accents = ["mauve"];
        size = "standard";
    })
];
environment.sessionVariables.GTK_THEME = "catppuccin-mocha-mauve-standard";
```

**ВАЖНО:** голый `catppuccin-gtk` дефолтится на frappe/blue. Используй `.override`.

## Swaybg — обои для niri

```bash
nix profile install nixpkgs#swaybg
```

В конфиге niri:
```kdl
spawn-at-startup "swaybg" "-i" "/path/to/wallpaper.png" "-m" "fill"
```

## Порядок загрузки EFI

```bash
sudo efibootmgr                           # список
sudo efibootmgr --bootorder 0001,0000     # переставить (NixOS первым)
```

## Права на serial-устройства

```nix
users.users.YOUR_USER.extraGroups = [ "dialout" ];
```

Или через udev (без перезапуска сессии):
```nix
services.udev.extraRules = ''
  SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666"
  SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666", GROUP="dialout"
'';
```

**Используй `:=`, а не `=`** — системные правила перекрывают простое `=`.
(VID `0483` / PID `5740` — это USB-CDC serial STMicroelectronics; так же определяется, например, FlipperZero.)

Проверить права и VID/PID воткнутого устройства:
```bash
ls -la /dev/ttyACM0                                          # ожидаем crw-rw-rw-
udevadm info -a -n /dev/ttyACM0 | grep -E 'idVendor|idProduct' | head -2
```

## Автомонтаж HDD (NTFS)

```bash
sudo blkid /dev/sda2    # узнать UUID
```

```nix
fileSystems."/mnt/data" = {
    device = "/dev/disk/by-uuid/YOUR_UUID";
    fsType = "ntfs-3g";
    options = ["uid=1000" "gid=100" "noatime"];
};
```

## Скриншоты: Grim + Slurp + Satty

```kdl
Print        { screenshot; }
Mod+Shift+S  { spawn "sh" "-c" "grim -g \"$(slurp)\" - | satty -f -"; }
```

## Fastfetch (вкус · пример)

```jsonc
{
  "logo": { "source": "NixOS_small", "padding": { "top": 1, "left": 2 } },
  "display": { "separator": " \u001b[38;2;203;166;247m→\u001b[0m ", "key": { "width": 12 } },
  "modules": [
    {"type": "title", "keyColor": "#CBA6F7"},
    {"type": "separator"},
    {"type": "os", "keyColor": "#CBA6F7"},
    {"type": "cpu", "keyColor": "#CBA6F7"},
    {"type": "gpu", "keyColor": "#CBA6F7"},
    {"type": "memory", "keyColor": "#CBA6F7"},
    {"type": "disk", "keyColor": "#CBA6F7"},
    {"type": "localip", "keyColor": "#CBA6F7"}
  ]
}
```

## Rebuild руками агента (полная автономность, осознанный риск)

Чтобы агент сам делал `nixos-rebuild switch` без пароля:
```nix
security.sudo.extraRules = [{
    users = ["YOUR_USER"];
    commands = [{ command = "ALL"; options = ["NOPASSWD"]; }];
}];
```

**Это осознанный выбор, а не недосмотр.** `command = "ALL"` + NOPASSWD даёт агенту
беспарольный `sudo` на ВСЁ. Так и задумано — ради ПОЛНОЙ автономности агента на СВОЕЙ
личной машине, с принятием рисков: ошибающийся или скомпрометированный агент получает
root целиком. Это НЕ для рабочих, общих или продовых машин.

Хочешь меньше рисков — сузь до одной команды (агент сможет только пересобирать систему):
```nix
commands = [{ command = "/run/current-system/sw/bin/nixos-rebuild"; options = ["NOPASSWD"]; }];
```

## См. также
- `nixos-agent-environment` — окружение и рабочие паттерны агента на NixOS
- `nixos-nix-ld-electron` — Electron-приложения и зависимости
- `nixos-streaming` — Sunshine/Moonlight
- `niri-hotkeys` — горячие клавиши niri
