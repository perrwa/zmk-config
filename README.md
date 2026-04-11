# ZMK Config

This repository contains configuration files for the **Corne-Cherry v3.0.1** keyboard using [ZMK Firmware](https://zmk.dev/). It includes keymaps, overlays, and shield definitions, as well as visual representations of the keymap.

## Hardware and Wireless Module

This configuration is designed for:

- **Corne-Cherry v3.0.1**
- **Raytac nRF52840** module (e.g., [MDBT50Q-RX](https://www.raytac.com/product/ins.php?index_id=89))
- **Nice!Nano v2** controllers

## Repository Structure

```
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       ├── build.yml
│       └── draw-keymaps-unified.yml
├── boards/
│   └── shields/
│       └── corne_dongle/
│           ├── Kconfig.shield
│           ├── corne_dongle.conf
│           └── corne_dongle.overlay
├── config/
│   ├── corne.conf
│   ├── corne.keymap
│   └── west.yml
├── keymap-drawer/
│   ├── corne.png
│   ├── corne.svg
│   ├── corne.yaml
│   ├── corne-unified.svg
│   ├── corne-unified.yaml
│   └── merge_layers.py
├── zephyr/
│   └── module.yml
├── build.yaml
├── keymap_drawer.config.yaml
├── Makefile
```

## Keymap Visualization

Keymap images are automatically generated using [keymap-drawer](https://github.com/caksoylar/keymap-drawer) by [caksoylar](https://github.com/caksoylar). The `draw-keymaps-unified.yml` workflow runs on pushes to keymap/config files and commits updated SVGs and YAML parse output to `keymap-drawer/`.

![Corne Keymap PNG](keymap-drawer/corne.png)


## Build Configurations

The `build.yaml` defines a **dongle setup** for GitHub Actions CI:

- **Raytac MDBT50Q-RX dongle** acts as the BLE central (`corne_dongle` shield)
- **Nice!Nano v2 halves** are both peripherals (overridden via `-DCONFIG_ZMK_SPLIT_ROLE_CENTRAL=n`)
- **`settings_reset`** firmware is included for both boards

Firmware builds on version tags (`v*`) or manual workflow dispatch.

## Files Overview

- `boards/shields/corne_dongle/` — Raytac dongle-specific shield, overlay, and Kconfig
- `config/` — Main Corne configuration (`corne.conf`) and keymap (`corne.keymap`)
- `keymap-drawer/` — [keymap-drawer](https://github.com/caksoylar/keymap-drawer) generated visualizations (SVG, YAML, PNG) and merge script
- `keymap-drawer/merge_layers.py` — Merges 4-layer parsed YAML into a single unified layer visualization
- `keymap_drawer.config.yaml` — keymap-drawer styling and parse configuration
- `zephyr/module.yml` — Registers this repo as a Zephyr module (sets `board_root`)
- `build.yaml` — GitHub Actions build matrix
- `Makefile` — DFU packaging and serial flashing for the Raytac dongle (requires `nrfutil`)

## Resources

- [ZMK Documentation](https://zmk.dev/docs/)
- [Corne Keyboard Info](https://github.com/foostan/crkbd)
- [Raytac Dongle ZMK Component (by rschenk)](https://github.com/rschenk/zmk-component-raytac-dongle)
- [keymap-drawer (by caksoylar)](https://github.com/caksoylar/keymap-drawer)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
