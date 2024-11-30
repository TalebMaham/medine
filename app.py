import os
from flask import Flask, json, jsonify, request, session, redirect, url_for, flash, render_template
from production.production import add_production, get_production, update_production, generate_report, clear_production, delete_production_by_date
from config import Config
from production.production_reader import get_daily_total
import requests
app = Flask(__name__)
app.config.from_object(Config)

API_BASE_URL = "http://localhost:8000/api/productions/"

users = {
    "abidine": "abidinepassword",
    "sidi": "sidipassword"
}

@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template("index.html", username=username)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            flash('Vous vous êtes connecté avec succès.')
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Vous vous êtes déconnecté avec succès.')
    return redirect(url_for('login'))

@app.route("/add_production", methods=["POST"])
def add_production_route():
    try:
        # Récupérer les données envoyées par la requête
        production_id = request.json.get("id")
        date = request.json.get("date")
        format_name = request.json.get("format_name")
        quantity = request.json.get("quantity")

        # Vérifier que les champs nécessaires sont présents
        if not (date and format_name and quantity is not None):
            return jsonify({"status": "error", "message": "Données incomplètes."}), 400

        if production_id:
            # Mise à jour de la production existante
            response = requests.patch(
                f"{API_BASE_URL}/{production_id}/",
                json={"date": date, "format_name": format_name, "quantity": quantity}
            )
        else:
            # Ajout d'une nouvelle production
            response = requests.post(
                API_BASE_URL,
                json={"date": date, "format_name": format_name, "quantity": quantity}
            )

        if response.status_code in (200, 201, 204):
            return jsonify({"status": "success", "message": "Opération réussie."}), response.status_code
        else:
            return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/get_production", methods=["GET"])
def get_production_route():
    try:
        # Récupérer les données brutes de l'API
        response = requests.get(API_BASE_URL)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Erreur lors de la récupération des données."}), response.status_code

        data = response.json()
        return jsonify(perform_calculations(data))
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def perform_calculations(data):
    """
    Effectue les calculs demandés (totaux journaliers, cumulés, pourcentages).
    """
    daily_totals = {}
    cumulative_totals = {}
    total_global = 0

    # Regrouper les données par date et format_name
    for production in data:
        date = production['date']
        format_name = production['format_name']
        quantity = production['quantity']

        # Totaux journaliers
        if date not in daily_totals:
            daily_totals[date] = {"formats": {}, "total": 0}

        if format_name not in daily_totals[date]["formats"]:
            daily_totals[date]["formats"][format_name] = 0

        daily_totals[date]["formats"][format_name] += quantity
        daily_totals[date]["total"] += quantity

        # Totaux cumulés
        if format_name not in cumulative_totals:
            cumulative_totals[format_name] = 0

        cumulative_totals[format_name] += quantity

        total_global += quantity

    # Calculer les pourcentages
    percentages = [
        {
            "format_name": format_name,
            "percentage": round((quantity / total_global) * 100, 2) if total_global > 0 else 0
        }
        for format_name, quantity in cumulative_totals.items()
    ]

    return {
        "daily_totals": daily_totals,
        "cumulative_totals": [{"format_name": k, "total_quantity": v} for k, v in cumulative_totals.items()],
        "percentages": percentages
    }


@app.route("/update_production", methods=["POST"])
def update_production_route():
    production_id = request.json.get("id")
    if not production_id:
        return jsonify({"status": "error", "message": "ID manquant"}), 400
    try:
        response = requests.put(
            f"{API_BASE_URL}/{production_id}/+",
            json=request.json
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/generate_report/<date>")
def generate_report_route(date):
    # Cette logique doit être réadaptée si Django doit aussi générer un rapport
    return jsonify({"status": "success", "message": f"Rapport généré pour {date}"}), 200

@app.route("/clear_production", methods=["POST"])
def clear_production_route():
    try:
        response = requests.delete(API_BASE_URL)
        return jsonify({"status": "success"}), 204
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/delete_production_by_date", methods=["DELETE"])
def delete_production_by_date_route():
    date = request.args.get("date")  # Récupérer la date depuis les paramètres de la requête
    if not date:
        return jsonify({"status": "error", "message": "Date manquante"}), 400

    try:
        # Envoyer la requête DELETE à l'API Django
        response = requests.delete(
            "http://localhost:8000/api/productions-delete-by-date/delete_by_date/",
            params={"date": date},
            timeout=10  # Ajouter un timeout explicite
        )
        
        if response.status_code == 204:
            return jsonify({"status": "success", "message": f"Productions supprimées pour la date {date}."}), 204
        else:
            # Retourner le message d'erreur de l'API Django
            return jsonify({"status": "error", "message": response.json()}), response.status_code

    except requests.ConnectionError:
        return jsonify({"status": "error", "message": "Impossible de se connecter au serveur Django."}), 500
    except requests.Timeout:
        return jsonify({"status": "error", "message": "La requête à l'API Django a expiré."}), 504
    except requests.RequestException as e:
        # Gestion générique pour les autres erreurs réseau
        return jsonify({"status": "error", "message": f"Erreur de réseau : {str(e)}"}), 500



@app.route('/daily-total', methods=['GET'])
def daily_total():
    date = request.args.get('date')
    if not date:
        return jsonify({"status": "error", "message": "Date is required"}), 400
    try:
        response = requests.get(f"{API_BASE_URL}?date={date}")
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

DATA_FILE_STOCK = "data_stock.json"
# Charger les données
def load_data(data_file="data_stock.json"):
    """Charge les données JSON depuis un fichier. Retourne un dictionnaire vide si le fichier est vide."""
    if not os.path.exists(data_file):
        return {}

    try:
        with open(data_file, "r") as file:
            content = file.read().strip()  # Supprimer les espaces blancs ou les lignes vides
            if not content:
                return {}  # Si le fichier est vide, retourner un dictionnaire vide
            return json.loads(content)  # Charger le contenu JSON
    except json.JSONDecodeError:
        # Si le fichier est corrompu, le considérer comme vide
        return {}


# Sauvegarder les données
def save_data(data):
    with open(DATA_FILE_STOCK, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/setStock', methods=['POST'])
def set_stock():
    data = load_data()
    request_data = request.json

    date = request_data.get("date")
    film = request_data.get("film")
    entry = request_data.get("entry")
    used = request_data.get("used")
    total_x = request_data.get("total_x")
    gaspiage = request_data.get("gaspiage")

    if not date or not film or entry is None or used is None or total_x is None or gaspiage is None:
        return jsonify({"status": "error", "message": "Tous les champs sont obligatoires"}), 400

    # Calcul du Stock initial (Stock cumulé de la date précédente)
    previous_date = max([d for d in data.keys() if d < date], default=None)
    stock_initial = data[previous_date]["stock_cumule"] if previous_date else 0

    # Calcul du Stock cumulé d'aujourd'hui
    stock_cumule = stock_initial + entry - used - gaspiage

    # Enregistrement des données dans le fichier
    data[date] = {
        "film": film,
        "entry": entry,
        "used": used,
        "total_x": total_x,
        "gaspiage": round(gaspiage, 2),
        "stock_initial": round(stock_initial, 2),
        "stock_cumule": round(stock_cumule, 2)
    }

    save_data(data)
    return jsonify({"status": "success", "message": "Stock enregistré avec succès"}), 200


@app.route('/getStock', methods=['GET'])
def get_stock():
    try:
        data = load_data()
        
        # Vérifier si les données sont vides
        if not data:
            return jsonify({"status": "success", "data": {}, "message": "Aucun stock disponible pour l'instant."}), 200

        # Trier les données par date
        sorted_data = dict(sorted(data.items(), key=lambda item: item[0]))
        
        return jsonify({"status": "success", "data": sorted_data}), 200
    except Exception as e:
        # Retourner une erreur générique en cas d'exception
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/clearStock', methods=['DELETE'])
def clear_stock():
    """Réinitialise le fichier JSON en mettant {}."""
    try:
        with open("data_stock.json", "w") as file:
            file.write("{}")  # Remplace le contenu par {}
        return jsonify({"status": "success", "message": "Le stock a été complètement supprimé."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erreur lors de la suppression : {str(e)}"}), 500


if __name__ == "__main__" : 
    app.run()