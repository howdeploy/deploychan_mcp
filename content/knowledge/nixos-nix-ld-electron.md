---
id: nixos-nix-ld-electron
name: 'NixOS: nix-ld и Electron-приложения'
summary: >-
  Как заставить Electron/Chromium-приложения работать на NixOS через nix-ld: полный
  список рантайм-зависимостей, NIXOS_OZONE_WL для Wayland, запуск Hermes Desktop с
  голосом, и SOCKS5-прокси по каждому инструменту (включая Zen Browser).
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, nix-ld, electron, hermes, proxy]
source: https://mcp.deploychan.webcam/docs
---

# Electron-приложения на NixOS (nix-ld)

Electron/Chromium-приложения — непропатченные бинарники: они ищут библиотеки в
`/usr/lib/`, которого на NixOS нет. Решение — `nix-ld` с полным набором рантайм-депсов.

## Полный набор рантайм-зависимостей Electron/Chromium

```nix
programs.nix-ld.libraries = with pkgs; [
    glib gtk3 nspr nss cups dbus at-spi2-core
    cairo pango gdk-pixbuf libdrm libxkbcommon
    libxshmfence libpulseaudio libgbm expat wayland
    zlib libpng libjpeg libwebp
    xorg.libxcb xorg.libXcomposite xorg.libXdamage
];
```

(Сначала `programs.nix-ld.enable = true;` — см. гайд `nixos-administration`.)

## Интеграция с Wayland
```nix
environment.sessionVariables.NIXOS_OZONE_WL = "1";
```

Для niri:
```kdl
environment { NIXOS_OZONE_WL "1" }
```

## Hermes Desktop на NixOS

### Предусловия
1. Electron-депсы через nix-ld (выше)
2. `NIXOS_OZONE_WL=1`
3. Голос: `portaudio` + `ffmpeg` в systemPackages, `LD_LIBRARY_PATH=/run/current-system/sw/lib`

### Автозапуск в niri
```kdl
spawn-at-startup "hermes" "desktop"
window-rule {
    match app-id="Hermes"
    open-maximized true
}
```

### Поддержка голоса
```bash
# В venv Hermes
uv pip install -e ".[voice]"
```
Конфиг:
```yaml
stt:
  enabled: true
  provider: groq   # или local
```
Env: `GROQ_API_KEY=<key>` в `~/.hermes/.env`

## SOCKS5-прокси по инструментам

Системный прокси на `127.0.0.1:10808` задаётся по каждому инструменту отдельно:
```bash
ALL_PROXY=socks5://127.0.0.1:10808 <command>
```

Zen Browser: пишем в `prefs.js`:
```
user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 10808);
user_pref("network.proxy.socks_version", 5);
user_pref("network.proxy.socks_remote_dns", true);
```

Python-инструменты: ставь `httpx[socks]` в venv.
