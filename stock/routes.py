from webargs import fields
from webargs.flaskparser import use_args
from flask import Flask, jsonify, request, session, redirect, url_for, flash, render_template

# Schéma de validation pour les données envoyées par le client
stock_args = {
    "date": fields.Str(required=True, description="La date du stock"),
    "film": fields.Str(required=True, description="Le type de film"),
    "entry": fields.Float(required=True, description="Quantité entrée"),
    "machine1": fields.Float(required=True, description="Production machine 1"),
    "machine2": fields.Float(required=True, description="Production machine 2"),
}

stock_data = {}

@use_args(stock_args, location="json")
def set_stock_route(args):
    """
    Endpoint pour enregistrer les données du stock localement.
    """
    try:
        # Extraire les données du schéma validé
        date = args['date']
        film = args['film']
        entry = args['entry']
        machine1 = args['machine1']
        machine2 = args['machine2']

        # Récupérer les données précédentes pour la date, sinon valeurs par défaut
        previous_data = stock_data.get(date, {})
        stock_initial = previous_data.get('stock_cumule', 0)

        # Calcul du total des machines et gaspillage
        total_x = machine1 + machine2
        gaspiage = total_x * 0.005

        # Calcul du stock cumulé
        stock_cumule = stock_initial + entry - total_x

        # Enregistrer les nouvelles données
        stock_data[date] = {
            "film": film,
            "entry": entry,
            "machine1": machine1,
            "machine2": machine2,
            "gaspiage": round(gaspiage, 2),
            "stock_initial": stock_initial,
            "stock_cumule": stock_cumule
        }

        return jsonify({"message": "Stock enregistré avec succès", "data": stock_data[date]}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500



def get_stock_route():
    """
    Endpoint pour récupérer les données du stock.
    """
    try:
        if not stock_data:
            return jsonify({"message": "Aucune donnée disponible"}), 404

        return jsonify({"data": stock_data}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500

def clear_stock_route():
    try:
        global stock_data
        stock_data.clear()  # Vide le dictionnaire
        return jsonify({"message": "Tous les stocks ont été supprimés avec succès."}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500
