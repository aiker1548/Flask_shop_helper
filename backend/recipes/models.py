from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from backend import db

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    measurement_unit = db.Column(db.String(200), nullable=False)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    color = db.Column(db.String(7), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(200), nullable=False)
    image = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(200), unique=False, nullable=False)
    text = db.Column(db.String, nullable=False)
    cooking_time = db.Column(db.Integer, default=1, nullable=False)

class IngredientsInRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    amount = db.Column(db.String(20), nullable=False)

    recipe = db.relationship('Recipe', foreign_keys=[recipe_id])
    ingredient = db.relationship('Ingredient', foreign_keys=[ingredient_id])

class TagsInRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

    recipe = db.relationship('Recipe', foreign_keys=[recipe_id])
    tag = db.relationship('Tag', foreign_keys=[tag_id])
