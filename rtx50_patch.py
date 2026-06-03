"""
rtx50_patch.py
Дополнение к gpu_specs.py: показатели карт RTX 50-й серии,
которых нет в исходном датасете 2023 года.

Значения откалиброваны по реальным обзорам (GamersNexus и др.)
для НАТИВНОГО рендеринга (без DLSS / Frame Generation) и приведены
к той же шкале, что и основной датасет, чтобы модель не экстраполировала.

Использование в gui.py:
    from gpu_specs import GPU_SPECS
    from rtx50_patch import RTX_50_SERIES
    GPU_SPECS.update(RTX_50_SERIES)
"""

RTX_50_SERIES = {
    "NVIDIA GeForce RTX 5060":    {"perf_1080": 130, "perf_1440": 96,  "perf_4k": 58,  "vram": 8.0,  "year": 2025.0},
    "NVIDIA GeForce RTX 5060 Ti": {"perf_1080": 155, "perf_1440": 116, "perf_4k": 70,  "vram": 16.0, "year": 2025.0},
    "NVIDIA GeForce RTX 5070":    {"perf_1080": 210, "perf_1440": 160, "perf_4k": 100, "vram": 12.0, "year": 2025.0},
    "NVIDIA GeForce RTX 5070 Ti": {"perf_1080": 255, "perf_1440": 195, "perf_4k": 123, "vram": 16.0, "year": 2025.0},
    "NVIDIA GeForce RTX 5080":    {"perf_1080": 300, "perf_1440": 230, "perf_4k": 147, "vram": 16.0, "year": 2025.0},
    "NVIDIA GeForce RTX 5090":    {"perf_1080": 358, "perf_1440": 278, "perf_4k": 176, "vram": 32.0, "year": 2025.0},
}
