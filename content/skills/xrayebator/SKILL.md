---
id: xrayebator
name: 'Xrayebator: свой VPN на VPS (Xray Reality)'
summary: >-
  Скилл KISA: интерактивный менеджер Xray Reality VPN на своём VPS. VLESS + REALITY —
  трафик неотличим от обычного HTTPS, без домена и сертификата, обходит DPI. Профили
  транспорта, добавление клиентов, HAPP-подписка. Чтобы агент ходил ресерчем и браузером
  через свой чистый выход мимо блокировок.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [vpn, xray, reality, vless, vps, censorship, proxy]
source: https://github.com/howdeploy/Xrayebator
description: >-
  Use when the user needs their own VPN/proxy on a VPS to bypass regional blocks or DPI so
  research APIs and browsers work through a clean exit. One-script Xray VLESS+REALITY
  installer and client manager.
license: MIT
---

# Xrayebator — свой VPN на VPS (Xray Reality)

Один скрипт поднимает и рулит **Xray Reality VPN** на твоём VPS. Технология — **VLESS +
REALITY**: трафик неотличим от обычного HTTPS-соединения к реальному сайту, без своего домена
и сертификата. Обычные протоколы (OpenVPN, WireGuard, Shadowsocks) DPI ловит по сигнатуре;
REALITY маскируется под легитимный TLS к чужому сайту — и потому не палится инспекцией пакетов.
Публичный: `howdeploy/Xrayebator` (v2.0), MIT.

> **Законность.** Свой VPN для приватности и доступа к своим сервисам легитимен во многих
> странах, но не везде. Это для личного доступа и research, а не для обхода закона. Проверь
> местные правила; ответственность за использование — на пользователе.

## Зачем это в deploychan

Часть сервисов недоступна из региона или палит публичные VPN. Гайды `agent-internet` и
`agent-voice` прямо на это ссылаются: research API, браузер, ElevenLabs, Stripe могут не
работать из-под региона. Xrayebator даёт **свой чистый выход** — агент ходит ресерчем и
браузером через твой VPS, а не через палёный публичный VPN. Свой VPN = свой контроль.

## Установка и управление

Скрипт интерактивный — запускается на чистом VPS от root:

```bash
git clone https://github.com/howdeploy/Xrayebator.git
cd Xrayebator
sudo bash xrayebator
```

Первый запуск — установка (ставит Xray-core, генерит ключи Reality, поднимает ноду). Каждый
следующий запуск — меню управления:

- **Установить** — развернуть Xray Reality на этом VPS.
- **Добавить клиента** — сгенерить нового клиента (VLESS-ссылка + QR).
- **Удалить** — убрать клиента или снести Xray.

Ключи и конфиг живут в `/usr/local/etc/xray/`. Маскировка настраивается через список SNI
(под какой реальный сайт мимикрирует соединение).

## Профили транспорта

v2.0 умеет несколько связок под разные условия сети и DPI:

- **VLESS + TCP + Reality + Vision** — базовая, самая стабильная.
- **+ Mux / + uTLS** — мультиплексирование и подмена TLS-отпечатка.
- **VLESS + XHTTP + Reality** — HTTP-обёртка, живучее там, где режут TCP.
- **VLESS + gRPC + Reality** — gRPC-транспорт (осторожно, медленнее).
- **VLESS PQ encryption** (`mlkem768x25519plus`) — пост-квантовое шифрование.

Плюс **HAPP-подписка** и мульти-роут профили: клиент получает подписку, а не одну ссылку.

## Клиенты

Импортируй сгенерированную VLESS-ссылку или скан QR:

| Платформа | Приложение |
|---|---|
| Android | v2rayNG, NekoBox, Hiddify, HAPP |
| iOS/macOS | Shadowrocket, V2BOX, Streisand, HAPP |
| Windows | v2rayN, Hiddify |
| Linux | v2rayA, Nekoray, Hiddify |

## Практика

- Бери VPS в чистом датацентре, вне заблокированного региона.
- Не ставь на тот же VPS палящиеся протоколы (OpenVPN/WireGuard) — некоторые провайдеры
  банят VPS, засветившийся на них. REALITY этого не требует.
- SNI-маскировку выбирай под доступный из твоего региона сайт: заблокировали текущий —
  меняешь SNI на другой, и соединение снова выглядит легитимным.
- Свой VPN нужен связке «агент + ресерч/браузер»: настроил выход — и `ALL_PROXY` /
  системный прокси направляют трафик агента через чистый экзит.
