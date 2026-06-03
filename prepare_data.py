"""
prepare_data.py

"""

import json
import csv
import re

INPUT = "gpus.json"
OUTPUT = "fps_data.csv"


def parse_number(value):
    if value is None:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    return float(match.group()) if match else None


def get_value(gpu, key):
    field = gpu.get(key)
    if isinstance(field, dict):
        return field.get("Value")
    return field


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    skipped = 0

    for gpu in data:
        gpu_name = gpu["Name"].strip()
        perf_1080 = parse_number(get_value(gpu, "Average 1080p Performance"))
        perf_1440 = parse_number(get_value(gpu, "Average 1440p Performance"))
        perf_4k   = parse_number(get_value(gpu, "Average 4K Performance"))
        vram      = parse_number(get_value(gpu, "Memory"))
        year      = parse_number(get_value(gpu, "Year"))

        if perf_1080 is None or vram is None:
            continue

        settings = gpu.get("Settings", {})
        for setting_level, setting_data in settings.items():
            resolutions = setting_data.get("Resolution", {})
            for resolution, res_data in resolutions.items():
                res_match = re.match(r"(\d+)x(\d+)", resolution)
                res_pixels = int(res_match.group(1)) * int(res_match.group(2)) if res_match else None

                for game in res_data.get("Games", []):
                    fps = parse_number(game.get("Avg_FPS"))
                    if fps is None:
                        skipped += 1
                        continue

                    rows.append({
                        "gpu": gpu_name,
                        "game": game["Game_Name"].strip(),
                        "settings": setting_level,
                        "resolution": resolution,
                        "res_pixels": res_pixels,
                        "perf_1080": perf_1080,
                        "perf_1440": perf_1440 if perf_1440 is not None else "",
                        "perf_4k": perf_4k if perf_4k is not None else "",
                        "vram": vram,
                        "year": year if year is not None else "",
                        "fps": fps,
                    })

    fieldnames = ["gpu", "game", "settings", "resolution", "res_pixels",
                  "perf_1080", "perf_1440", "perf_4k", "vram", "year", "fps"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Готово! Записано строк: {len(rows)}")
    print(f"Пропущено битых: {skipped}")
    print(f"Файл сохранён: {OUTPUT}")


if __name__ == "__main__":
    main()
