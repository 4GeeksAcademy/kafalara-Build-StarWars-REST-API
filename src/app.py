"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, PlanetFavorite, CharacterFavorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# [GET] /users Listar todos los usuarios del blog.
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    return jsonify({'msg': 'ok', 'data': users_serialized}), 200

# [GET] /users/<int:user_id>/favorites Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'User with id {user_id} not found'}), 404
    favorite_planets = []
    favorite_characters = []
    for fav in user.planet_favorites:
        favorite_planets.append(fav.planet.serialize())
    for fav in user.favorite_characters:
        favorite_characters.append(fav.character.serialize())
    favorites = {
        'planets': favorite_planets,
        'characters': favorite_characters
    }
    return jsonify({'msg': 'ok', 'data': favorites}), 200

# GET//character / Listar todos los personajes
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    all_characters = []
    for char in characters:
        all_characters.append(char.serialize())
    return jsonify({'msg': 'ok', 'data': all_characters}), 200

# GET/character/<int:character_id / Detalle de un personaje por ID
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({'msg': f'Character with id {character_id} not found'}), 404
    return jsonify({'msg': 'ok', 'data': character.serialize()}), 200

# [POST] /planet / Crear un nuevo planeta
@app.route('/planet', methods=['POST'])
def post_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'El campo name es obligatorio'}), 400
    if 'climate' not in body:
        return jsonify({'msg': 'El campo climate es obligatorio'}), 400
    if 'terrain' not in body:
        return jsonify({'msg': 'El campo terrain es obligatorio'}), 400    
    new_planet = Planet()
    new_planet.name = body['name']
    new_planet.climate = body['climate']
    new_planet.terrain = body['terrain']    
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({
        'msg': 'Planeta agregado con éxito',
        'data': new_planet.serialize()
    }), 201







# GET/planets / Listar todos los planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    all_planets = []
    for planet in planets:
        all_planets.append(planet.serialize())
    return jsonify({'msg': 'ok', 'data': all_planets}), 200

# GET/planets/<int:planet_id / Detalle de un planeta por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'msg': f'Planet with id {planet_id} not found'}), 404
    return jsonify({'msg': 'ok', 'data': planet.serialize()}), 200

# [POST] /favorite/planet/<int:planet_id>/<int:user_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_favorite_planet(planet_id, user_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({'msg': 'User or Planet not found'}), 404
    new_favorite = PlanetFavorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorite planet added successfully'}), 201

# [POST] /favorite/character/<int:character_id>/<int:user_id> Añade un nuevo people favorito al usuario actual con el id = people_id
@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['POST'])
def add_favorite_character(character_id, user_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)
    if not user or not character:
        return jsonify({'msg': 'User or Character not found'}), 404
    new_favorite = CharacterFavorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorite character added successfully'}), 201

# [DELETE] /favorite/planet/<int:planet_id>/<int:user_id> Elimina un planet favorito con el id = planet_id.
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    favorite = PlanetFavorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'msg': 'Favorite planet not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorite planet deleted successfully'}), 200

# [DELETE] /favorite/character/<int:character_id>/<int:user_id> Elimina un people favorito con el id = character_id.
@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_character(character_id, user_id):
    favorite = CharacterFavorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return jsonify({'msg': 'Favorite character not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'Favorite character deleted successfully'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
