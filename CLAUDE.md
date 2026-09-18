# Agent Instructions

Split Corne-Cherry v3.0.1 ZMK keyboard config. Nice!Nano v2 halves + Raytac MDBT50Q-RX or MDBT50Q-CX-40 dongle (BLE central). On `main`, the west manifest pins ZMK v0.3 + `rschenk/zmk-component-raytac-dongle@refs/heads/v0.3`; see [ZMK v0.4 Branch](#zmk-v04-branch) for what differs on `zmk-v0.4`.

## Build

No local build/test. Three GitHub Actions workflows:

- `build.yml` — CI on PRs to main, pushes to `zmk-v0.4`, + manual dispatch. Has a `check-changes` gate using `dorny/paths-filter` so the build job only runs when firmware-relevant files change (`config/`, `boards/`, `build.yaml`, `zephyr/`, `build.yml`) — applies to both the PR and push triggers; `workflow_dispatch` always builds. The `build-result` gate job always reports a status so required checks pass even when build is skipped.
- `release.yml` — push to main (with `paths-ignore` for keymap-drawer files) + manual dispatch. Builds firmware, then computes a `vYY.MM.N` tag (incrementing `N` off the latest matching tag via `git tag -l`) — or, on manual dispatch, uses the required `tag` input instead of computing one — and creates a draft prerelease. No tag push triggers it — the workflow creates the tag.
- `draw.yml` — push to main + PRs targeting main + manual dispatch. Only triggers on keymap-relevant path changes (`config/*.keymap`, `config/*.dtsi`, `keymap_drawer.config.yaml`, `keymap-drawer/merge_layers.py`). On main: opens a PR via `peter-evans/create-pull-request`. On branches: auto-commits via `stefanzweifel/git-auto-commit-action`. Layer names passed to `keymap parse` (`--layer-names Base Symbols Nav Numpad`) must be updated in this workflow if a layer is renamed in the keymap.

All build/release workflows call ZMK's reusable workflow (`zmkfirmware/zmk/.github/workflows/build-user-config.yml`). `build.yaml` defines the build matrix: `corne_dongle` on both Raytac boards, `corne_left`/`corne_right` on `nice_nano_v2`, and `settings_reset` on all three boards. There's no `cmake-args` central-role override in `build.yaml` — the halves get `CONFIG_ZMK_SPLIT_ROLE_CENTRAL=n` from a `.conf` file instead (see [Keyboard `.conf`](#keyboard-conf) below for which one, per branch), which applies regardless of board/shield.

`make dfu` packages firmware for dongle flashing (auto-generates `private.pem` via the `has_key` target if missing); `make flash` flashes interactively via serial; `make clean` removes generated `.zip` packages. Requires `nrfutil nrf5sdk-tools`.

### GitHub Actions Gotchas

- `timeout-minutes` is NOT valid on jobs that call reusable workflows via `uses:`. Only jobs with `runs-on` + `steps` support it. GitHub fails the entire workflow run at validation with no useful error message.
- When `paths-ignore` causes a workflow to skip entirely, required status checks never report — blocking PR merges. Use `dorny/paths-filter` inside the workflow instead, so the check always reports (as passed/skipped).
- `peter-evans/create-pull-request@v7` has built-in no-change detection — it won't create a PR or push if the working tree is clean. No need for explicit guards.
- West manifest `revision:` for a project is a raw git revision, so a bare name like `v0.3` is ambiguous if the remote has both a branch and a tag by that name — git's ref-resolution precedence prefers the tag, silently. `rschenk/zmk-component-raytac-dongle` has exactly this: a `v0.3` tag cut before the CX-40 board files were added, and a `v0.3` branch that has them. Pinning `revision: v0.3` fetched the stale tag and made `raytac_mdbt50q_cx_40` fail CMake's board resolution ("Invalid BOARD") while `raytac_mdbt50q_rx` (present since before the tag) built fine — a confusing signal since nothing in the repo's own files was wrong. Use the fully-qualified `refs/heads/<name>` (or `refs/tags/<name>`) to disambiguate whenever a remote might have overlapping branch/tag names.
- Don't assume a third-party module's default branch is `main` — `boardsource/wireless-corne_zmk_config`'s is `master`. `refs/heads/main` being fully-qualified doesn't help if the branch doesn't exist: `west update` failed with `fatal: couldn't find remote ref refs/heads/main` for *every* build target, not just the one using the new module — a bad project entry breaks `west update` for the whole manifest. Check the remote's actual default branch (`gh api repos/<owner>/<repo> --jq .default_branch`, or the branch listing) before pinning, don't infer it from convention.
- `dorny/paths-filter@v3` needs a real checkout for `push` events (it diffs with local git) but not for `pull_request` events (it queries the GitHub API instead). `check-changes` in `build.yml` ran fine on PRs for months with no `actions/checkout` step; the first push-triggered run (adding the `zmk-v0.4` push trigger) failed with `fatal: not a git repository`. Gate the checkout step on `github.event_name == 'push'` rather than adding it unconditionally, so PR runs stay fast.
- `dorny/paths-filter@v3`'s `base` input, left unset, defaults to the repo's *default branch* — not "since the last push" — unless `base` is explicitly the same ref as the one being pushed. On a branch that permanently diverges from `main` (like `zmk-v0.4`, where `config/west.yml`/`build.yaml`/etc. always differ), that default makes every push report changed firmware files regardless of what the push actually touched, silently defeating the skip-on-no-changes optimization. Set `base: ${{ github.event.before }}` explicitly for push events so it diffs against the actual pre-push commit.
- `release.yml`'s `git tag -l "${PREFIX}.*"` only sees tags that actually exist in the checked-out repo — and GitHub does **not** create a real tag ref for a *draft* release, only on publish. So a repeated push to `main` while a `vYY.MM.N` draft is pending keeps recomputing the same tag name (the draft's tag isn't visible to `git tag -l` yet) and `softprops/action-gh-release` overwrites that same draft's artifacts/notes rather than creating a new release. This also means **any** push to `main` reruns the full release pipeline and touches the pending draft, including doc-only commits — `paths-ignore` only excludes `keymap-drawer/**` and `keymap_drawer.config.yaml`, nothing else.

## Keymap

`config/corne.keymap` — Devicetree syntax, 4 layers: 0=QWERTY base, 1=symbols/F-keys, 2=nav/media, 3=numpad. Thumbs use `&mt` (mod-tap) and `&lt` (layer-tap). Layer access: hold Space→L1, hold Esc→L2, `&mo 3` from L1/L2.

Each layer has QMK-style comment blocks above `bindings` showing visual layout — keep in sync when editing.

`keymap-drawer/corne.yaml` is auto-generated by the `draw.yml` workflow — it is fully regenerated on each run (no manual tweaks preserved). The workflow also produces `corne-unified.yaml`/`corne-unified.svg` which collapses all layers into a single view via `keymap-drawer/merge_layers.py`. Styling config lives at `keymap_drawer.config.yaml` (repo root).

## Fork Context

This repo is Perry's fork (`perrwa/zmk-config`). Always target the fork for issues, PRs, and pushes unless explicitly told to work on upstream.

The dongle board component comes from `rschenk/zmk-component-raytac-dongle` — Perry's fork is `perrwa/zmk-component-raytac-dongle`. When creating issues or PRs for the dongle board, always use `perrwa/zmk-component-raytac-dongle`, not rschenk's upstream. Double-check the `--repo` flag on `gh` commands — the CLI may default to upstream if the local clone's `origin` points there.

### Multi-Board Context

`main` builds **both** dongle variants — `raytac_mdbt50q_rx` and `raytac_mdbt50q_cx_40` — from the single `rschenk/zmk-component-raytac-dongle` module pinned in `config/west.yml`; that module tree already ships board files for both, so no remote/module change is needed to add a dongle target, only a `build.yaml` matrix entry. Each board gets its own BLE advertise name via `boards/shields/corne_dongle/boards/<board>.conf` (Zephyr's shield-scoped board override, merged after `corne_dongle.conf`) — `perrwa-crkbd-rx` / `perrwa-crkbd-cx` (lowercase; `CONFIG_ZMK_KEYBOARD_NAME` has a 16-char limit) — so the two dongles are distinguishable when pairing.

### ZMK v0.4 Branch

`zmk-v0.4` is a long-lived branch tracking ZMK's `main` (v0.4 is unreleased; latest tag is v0.3.0) — used to verify HWMv2 board definitions ahead of the actual release. It builds the same matrix as `main` (both Raytac dongle boards + halves), not a different keyboard.

| | `main` | `zmk-v0.4` |
|---|---|---|
| ZMK revision | `v0.3` tag | `main` (moving, not reproducible) |
| Dongle module | `rschenk/zmk-component-raytac-dongle@refs/heads/v0.3` | `perrwa/zmk-component-raytac-dongle@refs/heads/main` |
| Board names | `raytac_mdbt50q_rx` / `raytac_mdbt50q_cx_40` | `mdbt50q_rx` / `mdbt50q_cx_40` / `nice_nano//zmk` (HWMv2 naming) |
| Protection | rulesets active — PR + `build-result` required | unprotected — direct commits, no PR/branch convention |
| Releases | `release.yml`, `vYY.MM.N` tags | none — CI build artifacts only |
| CI trigger | PR to main | push to branch |
| Extra hardware | none | BLE Corne (`blecorne_left`/`blecorne_right`) — see below |

Sync direction is `main` → `zmk-v0.4` via merge, never rebase (no force-push to either branch — the branch may have local work). Intentionally-divergent files — don't let a sync silently clobber these:

- `config/west.yml`, `build.yaml`
- `config/corne.conf` (on `main`, also carries `CONFIG_ZMK_SPLIT_ROLE_CENTRAL=n`); `config/corne_left.conf`/`corne_right.conf` (exist only on `zmk-v0.4`, carry that same setting there instead — see [Keyboard `.conf`](#keyboard-conf)). On `zmk-v0.4`, `corne.conf` also carries `CONFIG_ZMK_STUDIO=n` and blecorne-generalized wording that `main` doesn't need (`main` doesn't build blecorne).
- `config/blecorne*` (`.keymap`, `.conf`, `_left.conf`, `_right.conf`, `.overlay`) — exist only on `zmk-v0.4`; see [BLE Corne](#ble-corne-blecorne) below.
- `boards/shields/corne_dongle/boards/*.conf` — renamed, not just edited (`raytac_mdbt50q_{rx,cx_40}.conf` on `main` vs `mdbt50q_{rx,cx_40}.conf` on `zmk-v0.4`)
- both `release.yml` and `build.yml`'s `build-user-config.yml` ref (`@main` on this branch vs `@v0.3` on main)

`release.yml` is not branch-aware: its concurrency group is the literal string `release` and its tag search (`git tag -l`) is repo-global. If releases are ever enabled on `zmk-v0.4`, both need fixing first or a same-month release from each branch will collide into one `vYY.MM.N` sequence.

### BLE Corne (`blecorne`)

Boardsource Wireless Corne SMT — a second, independent keyboard on `zmk-v0.4`, not a variant of the Corne-Cherry. `zmk-v0.4`-only: its board files (`boardsource/wireless-corne_zmk_config`, pulled in as a west module in `config/west.yml`, board files only — no `import:`) use the HWMv2 format and that repo's own manifest pins ZMK `main`, so they won't build against `main`'s frozen `v0.3` tag. Unlike the dongle module, this one **isn't forked** — board-level defconfig/DTS changes would need an upstream PR or a fork, not a local edit.

It shares the same three-device dongle-central topology as the Corne-Cherry halves, and — because it uses the identical `foostan_corne_6col_layout` physical layout and 42-key transform (including the same `col-offset = <6>` right-half mirroring ZMK's own upstream `corne_right.overlay` uses, which is a correct pattern, not a bug) — the existing `corne_dongle` firmware images work for it unmodified. There's no `blecorne_dongle` shield or build target; a third physical Raytac dongle is flashed with the existing `corne_dongle` image and paired to blecorne independently (same BLE advertised name as whichever existing dongle shares its board type — fine, since pairing is by bond, not name).

`config/blecorne.keymap`, `blecorne.conf`, `blecorne_left.conf`, and `blecorne_right.conf` are symlinks to the corresponding `corne*` files — same bindings, same settings apply cleanly. This overrides `blecorne_left`'s own board `Kconfig.defconfig`, which (assuming standalone use) defaults it to `CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y` and enables Studio/USB; the symlinked `corne_left.conf`/`corne.conf` force `n` for the dongle-central topology (also disabling Studio there, since on-device keymap edits would diverge from git). `config/blecorne.overlay` is a real file — BLE Corne's devicetree defines no `ext_power` node, but `corne.keymap`'s Numpad layer binds `&ext_power EP_OFF`; it's wired to GPIO 0.31, the expansion-header VCC switch pin documented in Boardsource's README (real behavior — cuts power to expansion-header peripherals, not the MCU/BLE — since `zmk,ext-power-generic` requires `control-gpios`, so a true no-op isn't possible).

## Dongle BLE

`BT_MAX_CONN` and `BT_MAX_PAIRED` must equal `ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS` + desired BT profiles (see `boards/shields/corne_dongle/corne_dongle.conf`).

## Keyboard `.conf`

`config/corne.conf` holds half-side (peripheral) settings shared by both branches, applied regardless of board/shield: a 30-minute `CONFIG_ZMK_IDLE_SLEEP_TIMEOUT` (default is 15 min), RGB underglow/backlight disabled (inert no-ops — neither keyboard sharing this file defines a WS2812 or backlight devicetree node), `CONFIG_ZMK_BATTERY_REPORTING=y`, `CONFIG_ZMK_BLE_EXPERIMENTAL_CONN=y` to disable the 2M PHY for better 2.4 GHz interference resistance, and (on `zmk-v0.4` only) `CONFIG_ZMK_STUDIO=n` to override `blecorne_left`'s board default. On `zmk-v0.4`, `config/blecorne.conf` symlinks to this file — see [BLE Corne](#ble-corne-blecorne).

Two settings live in different places per branch:

- **`CONFIG_ZMK_SPLIT_ROLE_CENTRAL=n`**: on `main`, set in `config/corne.conf` itself. On `zmk-v0.4`, moved into `config/corne_left.conf` and `config/corne_right.conf` instead, because the stock corne shield's `Kconfig.defconfig` defaults `SHIELD_CORNE_LEFT` to central and `corne.conf` loads *before* the shield files — setting it there would end up overriding `corne_dongle.conf`'s `=y` on the dongle build.
- **`CONFIG_WS2812_STRIP=n`**: set on `main` alongside the other RGB settings. Deliberately absent on `zmk-v0.4` — under Zephyr 4.1 the symbol was split into per-bus names (`WS2812_STRIP_SPI` etc.), so setting the old bare name is now a hard Kconfig error rather than a harmless no-op.

## Testing Changes

There is no local ZMK toolchain. To test changes, push the branch and watch GitHub Actions: `gh run watch` or check the Actions tab. Debug CI failures by reading job logs with `gh run view --log-failed`.

## ZMK Build System

Board-specific defconfig and DTS changes must go in the board component module (`perrwa/zmk-component-raytac-dongle`), not in `config/boards/` within zmk-config. ZMK's reusable build workflow passes `-DZMK_CONFIG=/tmp/zmk-config/config` — board `.conf` file resolution follows Zephyr's rules for west modules, not the zmk-config `config/` directory.
