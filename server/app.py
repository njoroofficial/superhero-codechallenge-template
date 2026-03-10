#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Attach migration support to the app and SQLAlchemy instance.
migrate = Migrate(app, db)

# Initialize the SQLAlchemy extension with this Flask app.
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


@app.route('/heroes', methods=['GET'])
def get_heroes():
    # Fetch all heroes and return only the list fields expected by the client.
    heroes = Hero.query.all()
    heroes_dict = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]
    return make_response(jsonify(heroes_dict), 200)


@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    # Look up the hero; return 404 if it doesn't exist.
    hero = Hero.query.filter(Hero.id == id).first()
    if not hero:
        return make_response(jsonify({'error': 'Hero not found'}), 404)
    # Full hero payload includes hero_powers per model serialization rules.
    return make_response(jsonify(hero.to_dict()), 200)


@app.route('/powers', methods=['GET'])
def get_powers():
    # Fetch all powers and return only the list fields expected by the client.
    powers = Power.query.all()
    powers_dict = [
        power.to_dict(only=('id', 'name', 'description')) for power in powers
    ]
    return make_response(jsonify(powers_dict), 200)


@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_by_id(id):
    # Look up the power; return 404 if it doesn't exist.
    power = Power.query.filter(Power.id == id).first()
    if not power:
        return make_response(jsonify({'error': 'Power not found'}), 404)

    if request.method == 'GET':
        # Return the single power resource.
        return make_response(
            jsonify(power.to_dict(only=('id', 'name', 'description'))), 200
        )

    # PATCH: update the power description if present in the payload.
    data = request.get_json() or {}
    try:
        if 'description' in data:
            power.description = data['description']
        db.session.commit()
        return make_response(
            jsonify(power.to_dict(only=('id', 'name', 'description'))), 200
        )
    except ValueError:
        # Validation errors from the model return a 400.
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    # Create a new HeroPower from the request payload.
    data = request.get_json() or {}
    try:
        hero_power = HeroPower(
            strength=data.get('strength'),
            hero_id=data.get('hero_id'),
            power_id=data.get('power_id'),
        )
        db.session.add(hero_power)
        db.session.commit()
        # Full payload includes nested hero and power per serialization rules.
        return make_response(jsonify(hero_power.to_dict()), 200)
    except ValueError:
        # Validation errors from the model return a 400.
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
