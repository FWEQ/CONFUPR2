import argparse
import json
import os
import re
import sys
from typing import Any, Dict

EXPECTED_KEYS = {
    "package_name": str,
    "repo": str,
    "test_mode": bool,
    "version": str,
    "max_depth": int
}


class ConfigError(Exception):
    pass


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise ConfigError(f"Файл конфигурации не найден: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Ошибка разбора JSON: {e}")
    if not isinstance(data, dict):
        raise ConfigError("Ожидается JSON-объект (словарь) в корне файла конфигурации.")
    return data


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "yes", "1"):
            return True
        if v in ("false", "no", "0"):
            return False
    raise ConfigError(f"Невозможно привести к булеву типу: {value!r}")


def validate_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    validated = {}
    for key, expected_type in EXPECTED_KEYS.items():
        if key not in cfg:
            raise ConfigError(f"Отсутствует обязательный параметр: '{key}'")

    pn = cfg["package_name"]
    if not isinstance(pn, str) or not pn.strip():
        raise ConfigError("package_name должен быть непустой строкой.")
    validated["package_name"] = pn.strip()

    repo = cfg["repo"]
    if not isinstance(repo, str) or not repo.strip():
        raise ConfigError("repo должен быть непустой строкой (URL или путь к тестовому репозиторию).")
    validated["repo"] = repo.strip()

    try:
        validated["test_mode"] = coerce_bool(cfg["test_mode"])
    except ConfigError as e:
        raise ConfigError(f"test_mode: {e}")

    version = cfg["version"]
    if not isinstance(version, str) or not version.strip():
        raise ConfigError("version должен быть непустой строкой.") #

    md = cfg["max_depth"]
    if isinstance(md, (int, float)) and float(md).is_integer():
        md_int = int(md)
    elif isinstance(md, str) and md.strip().isdigit():
        md_int = int(md.strip())
    else:
        raise ConfigError("max_depth должен быть целым числом >= 1.")
    if md_int < 1:
        raise ConfigError("max_depth должен быть >= 1.")
    validated["max_depth"] = md_int

    return validated


def print_kv(cfg: Dict[str, Any]) -> None:
    for k, v in cfg.items():
        print(f"{k}={v}")


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("-c", "--config", default="config.json")
    return p


def main():
    parser = build_argparser()
    args = parser.parse_args()

    try:
        raw = load_json(args.config)
        cfg = validate_config(raw)
    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(3)

    print_kv(cfg) # только для этого этапа лоль


if __name__ == "__main__":
    main()
