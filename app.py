from flask import Flask, jsonify, request, session, redirect, url_for, flash, render_template
from config import Config
from datetime import datetime
from production.routes import (
    add_production_route,
    get_production_route,
    update_production_route,
    generate_report_route,
    clear_production_route,
    delete_production_by_date_route,
    daily_total,
)

from stock.routes import (
    set_stock_route,
    get_stock_route,
    clear_stock_route
)
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

API_BASE_URL = "http://localhost:8000/api/productions/"
API_BASE_URL  = "https://chri2.com/medineapi/api/productions/"
users = {
    "abidine": "abidinepassword",
    "sidi": "sidipassword"
}
connected_users = []  # Liste pour suivre les utilisateurs connectés avec leur date de connexion

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

            # Vérifie si l'utilisateur est déjà dans la liste
            user_exists = next((user for user in connected_users if user['username'] == username), None)
            if user_exists:
                user_exists['connected'] = True  # Met à jour le statut de connexion
                user_exists['login_time'] = datetime.now()  # Met à jour la date de connexion
            else:
                connected_users.append({
                    'username': username,
                    'connected': True,
                    'login_time': datetime.now(),
                    'logout_time': None
                })

            flash('Vous vous êtes connecté avec succès.')
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Nom d\'utilisateur déjà pris. Veuillez en choisir un autre.')
            return redirect(url_for('register'))
        
        users[username] = password
        flash('Inscription réussie. Connectez-vous maintenant.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        # Trouver l'utilisateur et mettre à jour son statut et la date de déconnexion
        user = next((user for user in connected_users if user['username'] == username), None)
        if user:
            user['connected'] = False  # Met à jour le statut de connexion
            user['logout_time'] = datetime.now()  # Met à jour la date de déconnexion

        session.pop('username', None)
        flash('Vous vous êtes déconnecté avec succès.')
    return redirect(url_for('login'))



@app.route('/connected-users', methods=['GET'])
def get_connected_users():
    """Retourne la liste des utilisateurs connectés et déconnectés"""
    return jsonify(connected_users)



# Routes pour la production
app.add_url_rule('/add_production', 'add_production', add_production_route, methods=['POST'])
app.add_url_rule('/get_production', 'get_production', get_production_route, methods=['GET'])
app.add_url_rule('/update_production', 'update_production', update_production_route, methods=['POST'])
app.add_url_rule('/generate_report/<date>', 'generate_report', generate_report_route, methods=['GET'])
app.add_url_rule('/clear_production', 'clear_production', clear_production_route, methods=['POST'])
app.add_url_rule('/delete_production_by_date', 'delete_production_by_date', delete_production_by_date_route, methods=['DELETE'])
app.add_url_rule('/daily-total', 'daily_total', daily_total, methods=['GET'])


app.add_url_rule('/set_stock', 'set_stock', set_stock_route, methods=['POST'])
app.add_url_rule('/get_stock', 'get_stock', get_stock_route, methods=['GET'])
app.add_url_rule('/clear_stock', 'clear_stock', clear_stock_route, methods= ['DELETE'])


if __name__ == "__main__":
    app.run()
