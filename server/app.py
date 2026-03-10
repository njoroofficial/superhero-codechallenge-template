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

# Add migration support to the app and SQLAlchemy instance.
migrate = Migrate(app, db)

# Initialize the SQLAlchemy extension with Flask app.
db.init_app(app)

#  home page route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Fetch all heroes and return and return their name and super name
@app.route('/heroes', methods=['GET'])
def get_heroes(): 
    heroes = Hero.query.all()
    heroes_dict = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]
    return make_response(jsonify(heroes_dict), 200)

# Get a hero by id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):  
    hero = Hero.query.filter(Hero.id == id).first()
    if not hero:
        return make_response(jsonify({'error': 'Hero not found'}), 404)
    return make_response(jsonify(hero.to_dict()), 200)

# Fetch all powers and return and return the name and description
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_dict = [
        power.to_dict(only=('id', 'name', 'description')) for power in powers
    ]
    return make_response(jsonify(powers_dict), 200)

# Get power by id
@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_by_id(id):
    power = Power.query.filter(Power.id == id).first()
    if not power:
        return make_response(jsonify({'error': 'Power not found'}), 404)

    # if method is GET we return the name and description
    if request.method == 'GET':
        return make_response(
            jsonify(power.to_dict(only=('id', 'name', 'description'))), 200
        )

    # if method is PATCH, update the power description 
    data = request.get_json() or {}
    try:
        if 'description' in data:
            power.description = data['description']
        db.session.commit()
        return make_response(
            jsonify(power.to_dict(only=('id', 'name', 'description'))), 200
        )
    except ValueError:
        # Validation errors.
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)


 # Create a new HeroPower
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json() or {}
    try:
        hero_power = HeroPower(
            strength=data.get('strength'),
            hero_id=data.get('hero_id'),
            power_id=data.get('power_id'),
        )
        db.session.add(hero_power)
        db.session.commit()
        # the return response to the client.
        response_data = {
            'id': hero_power.id,
            'hero_id': hero_power.hero_id,
            'power_id': hero_power.power_id,
            'strength': hero_power.strength,
            'hero': hero_power.hero.to_dict(only=('id', 'name', 'super_name')),
            'power': hero_power.power.to_dict(only=('id', 'name', 'description')),
        }
        return make_response(jsonify(response_data), 200)
    except ValueError:
        # Validation errors 
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
