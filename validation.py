def validate_city_name(city_name):
    """Check whether the city name is usable before calling the weather API."""

    if not isinstance(city_name, str):
        raise ValueError("City name must be a string.")

    city_name = city_name.strip()

    if not city_name:
        raise ValueError("City name cannot be empty.")

    if len(city_name) > 100:
        raise ValueError("City name is too long.")

    return city_name