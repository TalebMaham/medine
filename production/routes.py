from flask import jsonify, request
import requests
from requests.auth import HTTPBasicAuth
from .utils import perform_calculations

API_BASE_URL = "https://chri2.com/medineapi/api/productions/"
#API_BASE_URL = "http://127.0.0.1:8000/api/productions/"
AUTH = HTTPBasicAuth('sidi', 'sidipassword')  # Identifiants pour Basic Auth

def add_production_route():
    try:
        data = request.json
        production_id = data.get("id")
        endpoint = f"{API_BASE_URL}/{production_id}/" if production_id else API_BASE_URL
        response = requests.patch(endpoint, json=data, auth=AUTH) if production_id else requests.post(endpoint, json=data, auth=AUTH)

        if response.status_code in (200, 201, 204):
            return jsonify({"status": "success", "message": "Opération réussie."}), response.status_code
        return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_production_route():
    try:
        response = requests.get(API_BASE_URL, auth=AUTH)
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
        response = requests.put(f"{API_BASE_URL}/{production_id}/", json=request.json, auth=AUTH)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def generate_report_route(date):
    api_url = API_BASE_URL 
    try:
        response = requests.get(api_url, params={"date__lte": date}, auth=AUTH)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Erreur lors de la récupération des données"}), 500

        production_data = response.json()
        daily_data = {}
        cumulative_totals = {}
        total_global = 0

        for production in production_data:
            format_name = production["format_name"]
            quantity = production["quantity"]
            prod_date = production["date"]

            if prod_date == date:
                daily_data[format_name] = daily_data.get(format_name, 0) + quantity
            cumulative_totals[format_name] = cumulative_totals.get(format_name, 0) + quantity

        total_global = sum(cumulative_totals.values())
        percentages = {
            format_name: round((quantity / total_global) * 100, 2) if total_global > 0 else 0
            for format_name, quantity in cumulative_totals.items()
        }
        daily_total = sum(daily_data.values())

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
        response = requests.delete(API_BASE_URL, auth=AUTH)
        return jsonify({"status": "success"}), 204
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def delete_production_by_date_route():
    date = request.args.get("date")
    if not date:
        return jsonify({"status": "error", "message": "Date manquante"}), 400
    try:
        response = requests.delete(
            "https://chri2.com/medineapi/api/productions-delete-by-date/delete_by_date/",
            params={"date": date},
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 204:
            return jsonify({"status": "success", "message": f"Productions supprimées pour la date {date}."}), 204
        return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def daily_total():
    date = request.args.get('date')
    format_name = request.args.get('format_name')

    if not date:
        return jsonify({"status": "error", "message": "Date is required"}), 400
    if not format_name:
        return jsonify({"status": "error", "message": "Format name is required"}), 400

    try:
        response = requests.get(f"{API_BASE_URL}?date={date}&format_name={format_name}", auth=AUTH)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": response.json().get("message", "Unknown error")}), response.status_code
        print(f"response : {response.json()}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500
