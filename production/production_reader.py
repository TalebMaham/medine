import json
from flask import jsonify

# Charger les données de production
def load_data(data_file):
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Obtenir les données de production
def get_production(data_file):
    data = load_data(data_file)
    daily_totals = {}
    cumulative_totals = {}
    total_global = 0

    for date, formats in data.items():
        daily_total = 0
        for format_name, quantity in formats.items():
            if format_name not in cumulative_totals:
                cumulative_totals[format_name] = 0
            cumulative_totals[format_name] += quantity
            daily_total += quantity
            total_global += quantity

            if date not in daily_totals:
                daily_totals[date] = {}
            daily_totals[date][format_name] = quantity
        daily_totals[date]['total'] = daily_total

    percentages = {format_name: round((quantity / total_global) * 100, 2) if total_global > 0 else 0
                   for format_name, quantity in cumulative_totals.items()}

    return jsonify({
        "data": data,
        "daily_totals": daily_totals,
        "cumulative_totals": cumulative_totals,
        "total_global": total_global,
        "percentages": percentages
    })

# Générer un rapport de production
def generate_report(data_file, date):
    data = load_data(data_file)
    if date not in data:
        return jsonify({"status": "error", "message": "Date not found"}), 404

    # Production du jour spécifique
    daily_data = data[date]
    daily_total = sum(daily_data.values())

    # Calcul des totaux cumulés pour chaque produit jusqu'à la date spécifiée
    cumulative_totals = {}
    for day, formats in data.items():
        if day <= date:  # Inclure uniquement les jours jusqu'à la date demandée
            for format_name, quantity in formats.items():
                if format_name not in cumulative_totals:
                    cumulative_totals[format_name] = 0
                cumulative_totals[format_name] += quantity

    # Calcul du total global de toutes les productions cumulées
    total_global = sum(cumulative_totals.values())

    # Calcul des pourcentages de chaque produit par rapport au total global
    percentages = {
        format_name: round((quantity / total_global) * 100, 2) if total_global > 0 else 0
        for format_name, quantity in cumulative_totals.items()
    }

    # Création du rapport
    report = {
        "date": date,
        "daily_data": daily_data,
        "daily_total": daily_total,
        "cumulative_totals": cumulative_totals,
        "total_global": total_global,
        "percentages": percentages
    }
    return jsonify(report)




# Récupérer le daily_total pour une date spécifique
def get_daily_total(data_file, date):
    data = load_data(data_file)
    
    if date not in data:
        return jsonify({"status": "error", "message": "Date not found"}), 404

    # Calcul du total journalier pour la date spécifiée
    daily_data = data[date]
    daily_total = sum(daily_data.values())

    return jsonify({
        "date": date,
        "daily_total": daily_total
    })
