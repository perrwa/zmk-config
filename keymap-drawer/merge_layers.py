#!/usr/bin/env python3
"""Merge multi-layer keymap-drawer YAML into a single unified layer.

Maps each layer to a different legend position on each key:
  - Layer 0 (Base):    t (tap/center)
  - Layer 1 (Symbols): s (shifted/top)
  - Layer 2 (Nav):     h (hold/bottom)
  - Layer 3 (Numpad):  right

The base layer's hold value (modifier/layer indicator) goes to 'left'.
"""

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


def merge_layers(input_path):
    with open(input_path) as f:
        data = yaml.safe_load(f)

    layers = data.get("layers", {})
    layer_names = list(layers.keys())

    if len(layer_names) < 4:
        print(f"Error: expected 4 layers, found {len(layer_names)}", file=sys.stderr)
        sys.exit(1)

    base = layers[layer_names[0]]
    syms = layers[layer_names[1]]
    nav = layers[layer_names[2]]
    npad = layers[layer_names[3]]

    merged = []
    for i in range(len(base)):
        t = get_tap(base[i])
        left = get_hold(base[i])
        s = get_tap(syms[i]) if i < len(syms) else ""
        h = get_tap(nav[i]) if i < len(nav) else ""
        right = get_tap(npad[i]) if i < len(npad) else ""

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

    output = {"layout": data.get("layout", {}), "layers": {"perrwa/corne": merged}}

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
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <parsed-keymap.yaml>", file=sys.stderr)
        sys.exit(1)
    merge_layers(sys.argv[1])
