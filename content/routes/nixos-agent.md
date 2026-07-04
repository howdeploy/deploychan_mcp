---
id: nixos-agent
name: Поднять агента на NixOS
summary: >-
  Маршрут для тех, кто держит кодинг-агента на NixOS: пережить декларативное окружение
  (нет coreutils → Python-фолбэк), включить nix-ld для бинарников и Electron, настроить
  систему и рабочий стол. Собрано из реального daily-driving опыта KISA.
type: route
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, agent, hermes, прокачка, setup]
steps:
  - title: Окружение и рабочие паттерны
    action: read
    ref: nixos-agent-environment
    body: Пережить NixOS — нет coreutils в PATH, Python-фолбэк, реальные бинарники в /run/current-system/sw/bin, подключение MCP и управление Hermes.
  - title: nix-ld и Electron-приложения
    action: configure
    ref: nixos-nix-ld-electron
    body: Включить nix-ld, скормить рантайм-депсы Electron/Chromium, поднять Hermes Desktop с голосом и прокси.
  - title: Администрирование и рабочий стол
    action: configure
    ref: nixos-administration
    body: Цикл правки конфига и rebuild, desktop-стек (waybar/niri/fuzzel/dunst/GTK), EFI, serial, монтаж HDD, NOPASSWD-rebuild для автономного агента.
---

# Поднять агента на NixOS

NixOS ломает агентов, привыкших к обычному Linux: нет `cat`/`ls`/`find` в PATH,
непропатченные бинарники падают без библиотек, интерактивные команды виснут без TTY.
Этот маршрут — как пройти это по шагам и получить рабочего агента на NixOS. Собран из
реального опыта daily-driving, а не из документации.

> **Порядок с универсальным маршрутом.** Ты на NixOS? Сначала подними окружение (шаг 1) —
> без него универсальный маршрут `agent-onboarding` (личность → интернет → голос → память)
> будет спотыкаться о нехватку coreutils и битые бинарники. Платформа первой, характер
> агента — потом. Это НЕ значит, что nixos-agent важнее для всех: он нужен только тем, кто
> реально на NixOS.

## Три шага

1. **Окружение и паттерны** (`nixos-agent-environment`). Python как универсальный
   фолбэк, реальные бинарники через `/run/current-system/sw/bin`, симлинк `/bin/bash`,
   подключение MCP и управление Hermes (`mcp_servers`, `pty`, рестарт gateway).
2. **nix-ld и Electron** (`nixos-nix-ld-electron`). Включить `nix-ld`, дать рантайм-депсы
   Electron/Chromium, `NIXOS_OZONE_WL` для Wayland, поднять Hermes Desktop с голосом.
3. **Администрирование и рабочий стол** (`nixos-administration`). Декларативный цикл
   правки и `nixos-rebuild`, desktop-стек, EFI/serial/HDD, автономный rebuild под агента.

## Дополнительно

Не шаги маршрута, но из того же NixOS-пака — по потребности:
- `nixos-streaming` — стриминг рабочего стола (Sunshine/Moonlight, вплоть до Samsung TV).
- `niri-hotkeys` — референс горячих клавиш niri.

## Как идти

Дёрни `next_step("nixos-agent:1")` — получишь материалы первого шага, дальше по
`next_step_id`. На каждом шаге читай знание и применяй под свою машину: плейсхолдеры
(`YOUR_USER`, `YOUR_HOSTNAME`, `YOUR_UUID`, `<NIXOS_IP>`) заменяй на свои значения.
Любая установка — через дисциплину базового скилла `tailored-install`.
