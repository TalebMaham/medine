def perform_calculations(data):
    """
    Effectue les calculs sur les données de production.
    """
    daily_totals = {}
    cumulative_totals = {}
    total_global = 0

    for production in data:
        date, format_name, quantity = production['date'], production['format_name'], production['quantity']

        if date not in daily_totals:
            daily_totals[date] = {"formats": {}, "total": 0}
        daily_totals[date]["formats"].setdefault(format_name, 0)
        daily_totals[date]["formats"][format_name] += quantity
        daily_totals[date]["total"] += quantity

        cumulative_totals[format_name] = cumulative_totals.get(format_name, 0) + quantity
        total_global += quantity

    percentages = [
        {"format_name": k, "percentage": round((v / total_global) * 100, 2) if total_global else 0}
        for k, v in cumulative_totals.items()
    ]

    return {
        "daily_totals": daily_totals,
        "cumulative_totals": [{"format_name": k, "total_quantity": v} for k, v in cumulative_totals.items()],
        "percentages": percentages
    }
