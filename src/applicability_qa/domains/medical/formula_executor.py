from __future__ import annotations


def execute(calculator: str, entities: dict) -> tuple[float, str]:
    key = calculator.lower()
    if "body mass index" in key or key == "bmi":
        weight = float(entities.get("weight_kg", entities.get("weight")))
        height = float(entities.get("height_m", entities.get("height")))
        if height > 3:
            height /= 100
        return weight / height**2, "kg/m^2"
    if "mean arterial pressure" in key or key == "map":
        return (float(entities["systolic_bp"]) + 2 * float(entities["diastolic_bp"])) / 3, "mmHg"
    if "anion gap" in key:
        return float(entities["sodium"]) - float(entities["chloride"]) - float(entities["bicarbonate"]), "mEq/L"
    raise ValueError(f"Unsupported medical calculator: {calculator}")
