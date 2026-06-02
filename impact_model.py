def calculate_impacts(crude_price: float) -> dict[str, float]:
    """Return estimated downstream costs for a given crude oil price.

    Multipliers represent a simple simulation model:
    - transportation = crude_price * 0.32
    - food logistics = transportation * 0.45
    - flight tickets = transportation * 1.25
    - household energy = crude_price * 0.28
    """
    transportation = crude_price * 0.32
    food = transportation * 0.45
    flight_ticket = transportation * 1.25
    household_energy = crude_price * 0.28
    return {
        "Crude Oil": crude_price,
        "Transportation": transportation,
        "Food Logistics": food,
        "Flight Tickets": flight_ticket,
        "Household Energy": household_energy,
    }
