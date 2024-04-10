from flask import Flask, jsonify, request, Blueprint
from flask_restful import Api, Resource, fields, marshal_with
from .models import db, Ingredient, Tag, Recipe, IngredientsInRecipe, TagsInRecipe

app = Flask(__name__)
api = Blueprint('api_recipe', __name__, url_prefix='/api')

ingredient_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'measurement_unit': fields.String
}

tag_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'color': fields.String,
    'slug': fields.String
}

recipe_fields = {
    'id': fields.Integer,
    'author': fields.String,
    'image': fields.Integer,
    'name': fields.String,
    'text': fields.String,
    'cooking_time': fields.Integer,
    'ingredients': fields.List(fields.Nested(ingredient_fields)),
    'tags': fields.List(fields.Nested(tag_fields))
}

class IngredientResource(Resource):
    @marshal_with(ingredient_fields)
    def get(self, ingredient_id=None):
        if ingredient_id:
            ingredient = Ingredient.query.get_or_404(ingredient_id)
            return ingredient
        else:
            ingredients = Ingredient.query.all()
            return ingredients

    @marshal_with(ingredient_fields)
    def post(self):
        data = request.json
        new_ingredient = Ingredient(name=data['name'], measurement_unit=data['measurement_unit'])
        db.session.add(new_ingredient)
        db.session.commit()
        return new_ingredient, 201

    @marshal_with(ingredient_fields)
    def put(self, ingredient_id):
        data = request.json
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        ingredient.name = data['name']
        ingredient.measurement_unit = data['measurement_unit']
        db.session.commit()
        return ingredient, 200

    def delete(self, ingredient_id):
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        db.session.delete(ingredient)
        db.session.commit()
        return {'message': 'Ingredient deleted successfully'}, 200

class TagResource(Resource):
    @marshal_with(tag_fields)
    def get(self, tag_id=None):
        if tag_id:
            tag = Tag.query.get_or_404(tag_id)
            return tag
        else:
            tags = Tag.query.all()
            return tags

    @marshal_with(tag_fields)
    def post(self):
        data = request.json
        new_tag = Tag(name=data['name'], color=data['color'], slug=data['slug'])
        db.session.add(new_tag)
        db.session.commit()
        return new_tag, 201



class RecipeResource(Resource):
    @marshal_with(recipe_fields)
    def get(self, recipe_id=None):
        if recipe_id:
            recipe = Recipe.query.get_or_404(recipe_id)
            return recipe
        else:
            recipes = Recipe.query.all()
            return recipes

    @marshal_with(recipe_fields)
    def post(self):
        data = request.json
        ingredients_data = data.pop('ingredients', [])
        tags_data = data.pop('tags', [])
        
        new_recipe = Recipe(**data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.query.get_or_404(ingredient_data['id'])
            new_ingredient_in_recipe = IngredientsInRecipe(ingredient=ingredient, amount=ingredient_data['amount'], recipe=new_recipe)
            db.session.add(new_ingredient_in_recipe)

        for tag_data in tags_data:
            tag = Tag.query.get_or_404(tag_data['id'])
            new_tag_in_recipe = TagsInRecipe(tag=tag, recipe=new_recipe)
            db.session.add(new_tag_in_recipe)

        db.session.add(new_recipe)
        db.session.commit()
        return new_recipe, 201

    @marshal_with(recipe_fields)
    def put(self, recipe_id):
        data = request.json
        recipe = Recipe.query.get_or_404(recipe_id)
        recipe.author = data['author']
        recipe.image = data['image']
        recipe.name = data['name']
        recipe.text = data['text']
        recipe.cooking_time = data['cooking_time']
        
        ingredients_data = data.get('ingredients', [])
        tags_data = data.get('tags', [])

        # Удаляем все связанные ингредиенты и теги
        IngredientsInRecipe.query.filter_by(recipe_id=recipe_id).delete()
        TagsInRecipe.query.filter_by(recipe_id=recipe_id).delete()

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.query.get_or_404(ingredient_data['id'])
            new_ingredient_in_recipe = IngredientsInRecipe(ingredient=ingredient, amount=ingredient_data['amount'], recipe=recipe)
            db.session.add(new_ingredient_in_recipe)

        for tag_data in tags_data:
            tag = Tag.query.get_or_404(tag_data['id'])
            new_tag_in_recipe = TagsInRecipe(tag=tag, recipe=recipe)
            db.session.add(new_tag_in_recipe)

        db.session.commit()
        return recipe, 200

    def delete(self, recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return {'message': 'Recipe deleted successfully'},

# Добавление ресурсов в API
api.add_url_rule('/ingredients/<int:ingredient_id>/', view_func=IngredientResource.as_view('ingredient'), methods=['PUT', 'DELETE'])
api.add_url_rule('/ingredients/', view_func=IngredientResource.as_view('ingredients'), methods=['GET', 'POST'])

api.add_url_rule('/tags/<int:tag_id>/', view_func=TagResource.as_view('tag'), methods=['PUT', 'DELETE', 'GET'])
api.add_url_rule('/tags/', view_func=TagResource.as_view('tags'), methods=['GET', 'POST'])

api.add_url_rule('/recipes/<int:recipe_id>/', view_func=RecipeResource.as_view('recipe'), methods=['PUT', 'DELETE'])
api.add_url_rule('/recipes/', view_func=RecipeResource.as_view('recipes'), methods=["GET", "POST"])
