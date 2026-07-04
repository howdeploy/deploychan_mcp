---
id: nixos-streaming
name: 'NixOS: стриминг рабочего стола (Sunshine/Moonlight)'
summary: >-
  Реально настроенный стриминг рабочего стола на NixOS: Sunshine как хост, Moonlight
  как клиент. PC↔PC, второй монитор, и сайдлоад Moonlight на Samsung TV (Tizen) через
  Docker + sdb. Плюс почему Sunshine+Moonlight лучше RDP/VNC.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, streaming, sunshine, moonlight, samsung, tizen]
source: https://mcp.deploychan.webcam/docs
---

# Sunshine + Moonlight — стриминг рабочего стола на NixOS

Рабочий кейс: транслировать десктоп NixOS на другой ПК или на телевизор с низкой
задержкой. Хост — **Sunshine**, клиент — **Moonlight**. Ниже — как это поднять,
включая сайдлоад на Samsung TV.

## Включить Sunshine

```nix
services.sunshine = {
  enable = true;
  autoStart = true;
  capSysAdmin = true;
  openFirewall = true;   # порты 47984-48010
};
users.users.YOUR_USER.extraGroups = [ "uinput" "input" ];
boot.kernelModules = [ "uinput" ];
```

После `nixos-rebuild switch` — это systemd user-сервис. Веб-интерфейс на
`https://localhost:47990`.

## Moonlight — клиент PC ↔ PC

- Скачай Moonlight: https://moonlight-stream.org
- Автообнаружение Sunshine в LAN, либо добавь вручную: `<NIXOS_IP>:47989`
- Пара: Moonlight показывает PIN → открой `https://<NIXOS_IP>:47990` → вкладка PIN → введи
- Запусти «Desktop» для полного Wayland-стрима

### Второй монитор
Запусти Moonlight в фуллскрине на втором мониторе. Мышь/клавиатура с клиентского ПК
управляют десктопом NixOS.

### Хоткеи Moonlight
| Клавиши | Действие |
|---|---|
| Ctrl+Alt+Shift+X | Тумблер фуллскрина |
| Ctrl+Alt+Shift+Z | Тумблер захвата ввода |
| Ctrl+Alt+Shift+Q | Выйти из сессии |
| Ctrl+Alt+Shift+S | Оверлей статистики |

### Подводные камни
- Эксклюзивный фуллскрин захватывает оба монитора → Moonlight Settings → Display → целевой монитор
- Win-комбинации перехватывает ОС клиента → включи «Capture system keyboard shortcuts»

## Moonlight на Samsung TV (Tizen)

Официального приложения в Samsung Store нет — ставится сайдлоадом WGT-пакета.

### Способ A: Docker (проще всего)
```bash
docker run -it --rm ghcr.io/oneliberty/moonlight-chrome-tizen:samsung_wasm
sdb connect <TV_IP>
tizen install -n Moonlight.wgt
```

### Предусловия
1. Developer Mode на телевизоре: Apps → нажми `12345` → включи → задай Host PC IP
2. TV должен разрешать удалённую установку
3. Порт SDB: `26101`

### Готовые сборки
- OneLiberty/moonlight-chrome-tizen (Tizen 5.5+)
- brightcraft/moonlight-tizen (HDR, 4K, 120/144fps)

## Почему Sunshine+Moonlight, а не альтернативы
- RDP/VNC: хуже задержка, нет поддержки Wayland
- Barrier/Input Leap: делят ввод, но не видео
- <5ms энкод + <2ms сеть + <5ms декод на 60fps
