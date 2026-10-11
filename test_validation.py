from validation import validate_city_name
test_inputs = [
    "Udupi",
    "  Bengaluru  ",
    "",
    "   ",
    123,
]

for value in test_inputs:
    try:
        print(repr(value), "->", validate_city_name(value))
    except ValueError as err:
        print(repr(value), "-> REJECTED:", err)