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
    "dailyTotal" : fields.Float(required=True, description="Production de cette jounée"),
}

import requests
from requests.auth import HTTPBasicAuth
from flask import jsonify


# URL de l'API Django
API_BASE_URL = "http://127.0.0.1:8000/api/stock/"
API_BASE_URL = "https://chri2.com/medineapi/api/stock/"

# Identifiants d'authentification
AUTH = HTTPBasicAuth('sidi', 'sidipassword')

@use_args(stock_args, location="json")
def set_stock_route(args):
    """
    Endpoint pour enregistrer les données du stock via une requête POST vers l'API Django.
    """
    try:
        # Extraire les données du schéma validé
        data = {
            "date": args['date'],
            "film": args['film'],
            "entry": args['entry'],
            "machine1": args['machine1'],
            "machine2": args['machine2'],
            "daily_total": args['dailyTotal']
        }
        
        # Envoyer la requête POST à l'API Django avec l'authentification
        response = requests.post(API_BASE_URL, json=data, auth=AUTH)

        # Vérifiez si la réponse est réussie (statut 2xx)
        if response.status_code in [200, 201]:
            return jsonify({"message": "Stock enregistré avec succès", "data": response.json()}), 200
        else:
            return jsonify({"message": f"Erreur lors de l'enregistrement : {response.status_code}", "details": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500



def get_stock_route():
    """
    Endpoint pour récupérer les données du stock via une requête GET vers l'API Django.
    """
    try:
        # Envoyer la requête GET à l'API Django avec l'authentification
        response = requests.get(API_BASE_URL, auth=AUTH)

        # Vérifiez si la réponse est réussie (statut 2xx)
        if response.status_code == 200:
            return jsonify({"data": response.json()}), 200
        elif response.status_code == 404:
            return jsonify({"message": "Aucune donnée disponible"}), 404
        else:
            return jsonify({"message": f"Erreur lors de la récupération des données : {response.status_code}", "details": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500




def clear_stock_route():
    """
    Endpoint pour supprimer tous les stocks un par un via des requêtes DELETE.
    """
    try:
        # Étape 1 : Obtenez la liste de tous les stocks
        response = requests.get(API_BASE_URL, auth=AUTH)

        if response.status_code != 200:
            return jsonify({"message": f"Erreur lors de la récupération des stocks : {response.status_code}"}), response.status_code
        
        stock_list = response.json()  # Liste des stocks
        deleted_stocks = []

        # Étape 2 : Supprimez chaque stock individuellement
        for stock in stock_list:
            stock_id = stock['id']
            delete_url = f"{API_BASE_URL}{stock_id}/"
            delete_response = requests.delete(delete_url, auth=AUTH)
            
            if delete_response.status_code in [200, 204]:
                deleted_stocks.append(stock_id)
            else:
                return jsonify({"message": f"Erreur lors de la suppression du stock ID {stock_id}"}), delete_response.status_code

        return jsonify({"message": f"Les stocks {deleted_stocks} ont été supprimés avec succès."}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur interne : {str(e)}"}), 500
