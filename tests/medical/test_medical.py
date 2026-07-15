from applicability_qa.domains.medical.formula_executor import execute


def test_bmi():
    value, unit = execute("Body Mass Index (BMI)", {"weight_kg": 70, "height_m": 1.75})
    assert round(value, 2) == 22.86
    assert unit == "kg/m^2"
