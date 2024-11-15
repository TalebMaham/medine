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

# Ajouter des données de production
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
