from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['APPLICATION_ROOT'] = '/medine'

# Fichier JSON pour stocker les données de production
DATA_FILE = 'production_data.json'

# Charger les données de production
def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Sauvegarder les données de production
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

users = {
    "abidine" : "abidinepassword",
    "sidna" : "sidnapassword"
}



@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template("index.html",username=username)
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were successfully logged out')
    return redirect(url_for('login'))

@app.route("/add_production", methods=["POST"])
def add_production():
    data = load_data()
    # Récupère la date depuis la requête
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
    save_data(data)
    return jsonify({"status": "success"})

@app.route("/get_production", methods=["GET"])
def get_production():
    data = load_data()
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

@app.route("/update_production", methods=["POST"])
def update_production():
    data = load_data()
    date = request.json.get("date")
    format_name = request.json.get("format")
    quantity = request.json.get("quantity")
    
    if date in data and format_name in data[date]:
        data[date][format_name] = quantity
        save_data(data)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Data not found"}), 404

@app.route("/generate_report/<date>")
def generate_report(date):
    data = load_data()
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

@app.route("/clear_production", methods=["POST"])
def clear_production():
    # Supprime tout le contenu du fichier JSON en enregistrant un dictionnaire vide
    save_data({})
    return jsonify({"status": "success", "message": "Toutes les données de production ont été supprimées."})


@app.route("/delete_production_by_date", methods=["POST"])
def delete_production_by_date():
    data = load_data()
    # Récupère la date depuis la requête
    date = request.json.get("date")

    if not date:
        return jsonify({"status": "error", "message": "Date manquante."}), 400

    if date in data:
        # Supprime les données pour la date spécifiée
        del data[date]
        save_data(data)
        return jsonify({"status": "success", "message": f"Données supprimées pour la date {date}."})
    else:
        return jsonify({"status": "error", "message": "Date non trouvée dans les données."}), 404



if __name__ == "__main__":
    app.run(debug=True)
