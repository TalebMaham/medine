from flask import Flask, jsonify, request, session, redirect, url_for, flash, render_template
from config import Config
from production.routes import (
    add_production_route,
    get_production_route,
    update_production_route,
    generate_report_route,
    clear_production_route,
    delete_production_by_date_route,
    daily_total,
)
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

API_BASE_URL = "http://localhost:8000/api/productions/"
users = {
    "abidine": "abidinepassword",
    "sidi": "sidipassword"
}

# Routes liées à l'authentification et à la session utilisateur
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

# Routes pour la production
app.add_url_rule('/add_production', 'add_production', add_production_route, methods=['POST'])
app.add_url_rule('/get_production', 'get_production', get_production_route, methods=['GET'])
app.add_url_rule('/update_production', 'update_production', update_production_route, methods=['POST'])
app.add_url_rule('/generate_report/<date>', 'generate_report', generate_report_route, methods=['GET'])
app.add_url_rule('/clear_production', 'clear_production', clear_production_route, methods=['POST'])
app.add_url_rule('/delete_production_by_date', 'delete_production_by_date', delete_production_by_date_route, methods=['DELETE'])
app.add_url_rule('/daily-total', 'daily_total', daily_total, methods=['GET'])

# Routes pour le stock
DATA_FILE_STOCK = "data_stock.json"

def load_data(data_file="data_stock.json"):
    """Charge les données JSON depuis un fichier. Retourne un dictionnaire vide si le fichier est vide."""
    if not os.path.exists(data_file):
        return {}
    try:
        with open(data_file, "r") as file:
            content = file.read().strip()
            return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}

def save_data(data, data_file="data_stock.json"):
    """Sauvegarde les données JSON dans un fichier."""
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

stock_data = {}

@app.route('/setStock', methods=['POST'])
def set_stock():
    try:
        data = request.get_json()

        # Validation des champs
        required_fields = ['date', 'film', 'entry', 'used', 'total_x', 'gaspiage']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Champs manquants ou invalides"}), 400

        date = data['date']
        film = data['film']
        entry = data['entry']
        used = data['used']
        total_x = data['total_x']
        gaspiage = data['gaspiage']

        # Calculs : Stock initial et stock cumulé
        stock_initial = stock_data.get(date, {}).get('stock_cumule', 0) if date in stock_data else 0
        stock_cumule = stock_initial + entry - used

        # Enregistrement dans le stockage temporaire
        stock_data[date] = {
            "film": film,
            "entry": entry,
            "used": used,
            "total_x": total_x,
            "gaspiage": gaspiage,
            "stock_initial": stock_initial,
            "stock_cumule": stock_cumule
        }

        return jsonify({"message": "Stock enregistré avec succès", "data": stock_data[date]}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500

@app.route('/getStock', methods=['GET'])
def get_stock():
    try:
        if not stock_data:
            return jsonify({"message": "Aucun stock disponible"}), 404

        return jsonify({"data": stock_data}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500


@app.route('/clearStock', methods=['DELETE'])
def clear_stock():
    try:
        global stock_data
        stock_data.clear()  # Vide le dictionnaire
        return jsonify({"message": "Tous les stocks ont été supprimés avec succès."}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500


if __name__ == "__main__":
    app.run()
