import json
from flask import jsonify, request

# Charger les données de production
def load_data(data_file):
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Sauvegarder les données de production
def save_data(data_file, data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

# Routes pour les opérations liées à la production
def add_production(data_file):
    data = load_data(data_file)
    date = request.json.get("date")
    format_name = request.json.get("format")
    quantity = int(request.json.get("quantity"))
    
    if not date:
        return jsonify({"status": "error", "message": "Date manquante."}), 400

    if date not in data:
        data[date] = {}
    if format_name not in data[date]:
        data[date][format_name] = 0
    
    data[date][format_name] += quantity
    save_data(data_file, data)
    return jsonify({"status": "success"})

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
# Mettre à jour des données de production
def update_production(data_file):
    data = load_data(data_file)
    date = request.json.get("date")
    format_name = request.json.get("format")
    quantity = request.json.get("quantity")
    
    if date in data and format_name in data[date]:
        data[date][format_name] = quantity
        save_data(data_file, data)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 404

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

# Supprimer toutes les données
def clear_production(data_file):
    save_data(data_file, {})
    return jsonify({"status": "success", "message": "Toutes les données de production ont été supprimées."})

# Supprimer les données d'une date spécifique
def delete_production_by_date(data_file):
    data = load_data(data_file)
    date = request.json.get("date")

    if not date:
        return jsonify({"status": "error", "message": "Date manquante."}), 400

    if date in data:
        del data[date]
        save_data(data_file, data)
        return jsonify({"status": "success", "message": f"Données supprimées pour la date {date}."})
    else:
        return jsonify({"status": "error", "message": "Date non trouvée dans les données."}), 404
