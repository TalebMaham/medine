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


app.add_url_rule('/set_stock', 'set_stock', set_stock_route, methods=['POST'])
app.add_url_rule('/get_stock', 'get_stock', get_stock_route, methods=['GET'])
app.add_url_rule('/clear_stock', 'clear_stock', clear_stock_route, methods= ['DELETE'])


if __name__ == "__main__":
    app.run()
