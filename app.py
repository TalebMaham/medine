import os
from flask import Flask, json, jsonify, request, session, redirect, url_for, flash, render_template
from production.production import add_production, get_production, update_production, generate_report, clear_production, delete_production_by_date
from config import Config
from production.production_reader import get_daily_total

app = Flask(__name__)
app.config.from_object(Config)

users = {
    "abidine": "abidinepassword",
    "sidna": "sidnapassword"
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
    return add_production(app.config['DATA_FILE'])

@app.route("/get_production", methods=["GET"])
def get_production_route():
    return get_production(app.config['DATA_FILE'])

@app.route("/update_production", methods=["POST"])
def update_production_route():
    return update_production(app.config['DATA_FILE'])

@app.route("/generate_report/<date>")
def generate_report_route(date):
    return generate_report(app.config['DATA_FILE'], date)

@app.route("/clear_production", methods=["POST"])
def clear_production_route():
    return clear_production(app.config['DATA_FILE'])

@app.route("/delete_production_by_date", methods=["POST"])
def delete_production_by_date_route():
    return delete_production_by_date(app.config['DATA_FILE'])


@app.route('/daily-total', methods=['GET'])
def daily_total():
    data_file = app.config['DATA_FILE']
    date = request.args.get('date')
    
    if not date:
        return jsonify({"status": "error", "message": "Date is required"}), 400
    
    return get_daily_total(data_file, date)


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