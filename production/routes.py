from flask import jsonify, request
import requests
from .utils import perform_calculations

API_BASE_URL = "http://localhost:8000/api/productions/"

def add_production_route():
    try:
        data = request.json
        production_id = data.get("id")
        endpoint = f"{API_BASE_URL}/{production_id}/" if production_id else API_BASE_URL
        response = requests.patch(endpoint, json=data) if production_id else requests.post(endpoint, json=data)

        if response.status_code in (200, 201, 204):
            return jsonify({"status": "success", "message": "Opération réussie."}), response.status_code
        return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_production_route():
    try:
        response = requests.get(API_BASE_URL)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Erreur lors de la récupération des données."}), response.status_code
        return jsonify(perform_calculations(response.json()))
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def update_production_route():
    production_id = request.json.get("id")
    if not production_id:
        return jsonify({"status": "error", "message": "ID manquant"}), 400
    try:
        response = requests.put(f"{API_BASE_URL}/{production_id}/", json=request.json)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def generate_report_route(date):
    # URL de l'API Django pour récupérer les données de production
    api_url = "http://localhost:8000/api/productions/"
    
    try:
        # Récupération des données de l'API pour la date spécifiée et les jours précédents
        response = requests.get(api_url, params={"date__lte": date})  # `date__lte` pour inclure les dates <= aujourdhui
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Erreur lors de la récupération des données"}), 500
        
        production_data = response.json()  # Données brutes depuis l'API
        
        # Initialisation des structures de données
        daily_data = {}
        cumulative_totals = {}
        total_global = 0

        # Calcul des données
        for production in production_data:
            format_name = production["format_name"]
            quantity = production["quantity"]
            prod_date = production["date"]
            
            # Calcul des données journalières
            if prod_date == date:
                daily_data[format_name] = daily_data.get(format_name, 0) + quantity
            
            # Calcul des totaux cumulés
            cumulative_totals[format_name] = cumulative_totals.get(format_name, 0) + quantity
        
        # Calcul du total global
        total_global = sum(cumulative_totals.values())

        # Calcul des pourcentages
        percentages = {
            format_name: round((quantity / total_global) * 100, 2) if total_global > 0 else 0
            for format_name, quantity in cumulative_totals.items()
        }

        # Total du jour
        daily_total = sum(daily_data.values())

        # Création de la réponse JSON
        response_data = {
            "status": "success",
            "date": date,
            "daily_total": daily_total,
            "daily_data": daily_data,
            "cumulative_totals": cumulative_totals,
            "percentages": percentages,
            "total_global": total_global
        }

        return jsonify(response_data), 200

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Erreur réseau : {str(e)}"}), 500
    except Exception as e:
      return jsonify({"status": "error", "message": f"Erreur interne : {str(e)}"}), 500

def clear_production_route():
    try:
        response = requests.delete(API_BASE_URL)
        return jsonify({"status": "success"}), 204
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def delete_production_by_date_route():
    date = request.args.get("date")
    if not date:
        return jsonify({"status": "error", "message": "Date manquante"}), 400
    try:
        response = requests.delete(
            "http://localhost:8000/api/productions-delete-by-date/delete_by_date/",
            params={"date": date},
            timeout=10
        )
        if response.status_code == 204:
            return jsonify({"status": "success", "message": f"Productions supprimées pour la date {date}."}), 204
        return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def daily_total():
    date = request.args.get('date')
    if not date:
        return jsonify({"status": "error", "message": "Date is required"}), 400
    try:
        response = requests.get(f"{API_BASE_URL}?date={date}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500
