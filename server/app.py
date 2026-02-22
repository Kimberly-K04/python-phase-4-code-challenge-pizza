#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "address": r.address}
        for r in restaurants
    ])

# GET /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return {"error": "Restaurant not found"}, 404

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                } if rp.pizza else None
            } for rp in restaurant.restaurant_pizzas
        ]
    })

# DELETE
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return {"error": "Restaurant not found"}, 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "ingredients": p.ingredients}
        for p in pizzas
    ])

# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json() or {}

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    errors = []

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    if not pizza:
        errors.append(f"Pizza with id {pizza_id} does not exist")
    if not restaurant:
        errors.append(f"Restaurant with id {restaurant_id} does not exist")
    if price is None:
        errors.append("Price is required")
    elif not (1 <= price <= 30):
        errors.append("Price must be between 1 and 30")

    if errors:
        return {"errors": ["validation errors"]}, 400

    restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
    "id": restaurant_pizza.id,
    "price": restaurant_pizza.price,
    "pizza_id": restaurant_pizza.pizza_id,
    "restaurant_id": restaurant_pizza.restaurant_id,
    "pizza": {
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } if pizza else None,
    "restaurant": {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } if restaurant else None
}), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)