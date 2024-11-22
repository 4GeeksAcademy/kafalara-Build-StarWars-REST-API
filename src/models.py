from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#USUARIO
class User(db.Model):
    __tablename__= 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

    planet_favorites = db.relationship('PlanetFavorite', back_populates='user')
    favorite_characters = db.relationship('CharacterFavorite', back_populates='user')

    def __repr__(self):
         return f'Usuario {self.email} y id {self.id}'
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username, 
            "email": self.email,
            "is_active": self.is_active
        }

    
#PERSONAJES
class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    planet_id_relationship = db.relationship('Planet', back_populates='people')

    def __repr__(self):
        return f'Character {self.id} with ID {self.name}'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }

#PLANETAS
class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    climate = db.Column(db.String(60), nullable=False)
    terrain = db.Column(db.String(50), nullable=False)

    people = db.relationship('Character', back_populates='planet_id_relationship')
    favorite_planets = db.relationship('PlanetFavorite', back_populates='planet')

    def __repr__(self):
        return f'Planet {self.id} con nombre {self.name} Clima {self.climate} y Terrain {self.terrain}'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain
        }

#PLANETAS_FAVORITOS
class PlanetFavorite(db.Model):
    __tablename__ = 'planet_favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    

    user = db.relationship('User', back_populates='planet_favorites')
    planet = db.relationship('Planet', back_populates='favorite_planets')

    def __repr__(self):
        return f'<PlanetFavorite {self.id} - User {self.user_id} - Planet {self.planet_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "planet": self.planet.serialize()
        }

#PERSONAJES_FAVORITOS
class CharacterFavorite(db.Model):
    __tablename__ = 'character_favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    
    user = db.relationship('User', back_populates='favorite_characters')
    character = db.relationship('Character')

    def __repr__(self):
        return f'Al usuario {self.user_id} tiene como personaje favorito {self.character_id}'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "character": self.character.serialize()
        }
    
def to_dict(self):
        return {}