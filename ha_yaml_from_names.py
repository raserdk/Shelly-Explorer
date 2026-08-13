from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console

from shelly_explorer.homeassistant import generate_ha_modbus_multi_yaml

console = Console()


def load_name_map(path: str) -> dict[str, str]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")

    if file_path.suffix.lower() == ".json":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("Name mapping JSON must be an object with IP-to-name entries.")
        return {str(key): str(value) for key, value in payload.items()}

    names: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f'Invalid names file line {line_number}: expected "IP: Name"')
        key = key.strip().strip("\"'")
        value = value.strip().strip("\"'")
        if key and value:
            names[key] = value
    return names


def sort_ip_key(host: str) -> tuple[Any, ...]:
    try:
        return tuple(int(part) for part in host.split("."))
    except ValueError:
        return (host,)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Home Assistant Modbus YAML from a names file.")
    parser.add_argument("--names", required=True)
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--out")
    args = parser.parse_args()

    name_map = load_name_map(args.names)
    if not name_map:
        console.print("[yellow]No devices found in names file[/yellow]")
        return

    yaml_devices = [
        (host, name, None)
        for host, name in sorted(name_map.items(), key=lambda item: sort_ip_key(item[0]))
    ]

    yaml_text = generate_ha_modbus_multi_yaml(yaml_devices, port=args.port)

    if args.out:
        Path(args.out).write_text(yaml_text, encoding="utf-8")
        console.print(f"[green]Wrote Home Assistant YAML to {args.out}[/green]")
        console.print(f"[green]Included {len(yaml_devices)} devices from {args.names}[/green]")
        return

    print(yaml_text, end="")


if __name__ == "__main__":
    main()
