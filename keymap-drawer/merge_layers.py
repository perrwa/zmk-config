#!/usr/bin/env python3
"""Merge multi-layer keymap-drawer YAML into a single unified layer.

Maps each layer to a different legend position on each key:
  - Layer 0 (Base):    t (tap/center)
  - Layer 1 (Symbols): s (shifted/top)
  - Layer 2 (Nav):     h (hold/bottom)
  - Layer 3 (Numpad):  right

The base layer's hold value (modifier/layer indicator) goes to 'left'.
"""

import argparse
import sys
import yaml


def get_tap(key):
    """Extract tap value from a key spec (string or dict)."""
    if isinstance(key, str):
        return key
    if isinstance(key, dict):
        if key.get("type") == "held":
            return ""
        return key.get("t", key.get("tap", ""))
    return ""


def get_hold(key):
    """Extract hold value from a key spec."""
    if isinstance(key, dict):
        return key.get("h", key.get("hold", ""))
    return ""


def merge_layers(input_path, output_layer="Unified"):
    with open(input_path) as f:
        data = yaml.safe_load(f)

    layers = data.get("layers", {})
    expected = ["Base", "Symbols", "Nav", "Numpad"]
    actual = set(layers.keys())

    missing = [n for n in expected if n not in actual]
    unexpected = sorted(actual - set(expected))
    if missing or unexpected:
        errors = []
        if missing:
            errors.append(f"missing: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected: {', '.join(unexpected)}")
        print(
            f"Error: expected layers {expected}; {'; '.join(errors)}",
            file=sys.stderr,
        )
        sys.exit(1)

    base = layers["Base"]
    syms = layers["Symbols"]
    nav = layers["Nav"]
    npad = layers["Numpad"]

    # Validate all layers have the same number of keys
    for name, layer in [("Symbols", syms), ("Nav", nav), ("Numpad", npad)]:
        if len(layer) != len(base):
            print(
                f"Error: layer length mismatch: 'Base' has {len(base)} keys "
                f"but '{name}' has {len(layer)}",
                file=sys.stderr,
            )
            sys.exit(1)

    merged = []
    for i in range(len(base)):
        t = get_tap(base[i])
        left = get_hold(base[i])
        s = get_tap(syms[i])
        h = get_tap(nav[i])
        right = get_tap(npad[i])

        key = {}
        if t:
            key["t"] = str(t)
        if s:
            key["s"] = str(s)
        if h:
            key["h"] = str(h)
        if left:
            key["left"] = str(left)
        if right:
            key["right"] = str(right)

        if list(key.keys()) == ["t"]:
            merged.append(key["t"])
        elif not key:
            merged.append("")
        else:
            merged.append(key)

    output = {"layout": data.get("layout", {}), "layers": {output_layer: merged}}

    if "draw_config" in data:
        output["draw_config"] = data["draw_config"]
    if "combos" in data:
        output["combos"] = data["combos"]

    yaml.dump(
        output,
        sys.stdout,
        default_flow_style=None,
        allow_unicode=True,
        sort_keys=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge multi-layer keymap-drawer YAML into a single unified layer."
    )
    parser.add_argument("input", help="Path to parsed keymap YAML")
    parser.add_argument(
        "--output-layer",
        default="Unified",
        help="Name for the merged output layer (default: Unified)",
    )
    args = parser.parse_args()
    merge_layers(args.input, output_layer=args.output_layer)
