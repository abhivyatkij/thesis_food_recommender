from owlready2 import *
import os

owl_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline', 'nutri_ifct.owl')

try:
    onto = get_ontology("file://" + owl_file_path ).load()
    print("Ontology loaded successfully.")
except FileNotFoundError:
    print(f"Error: Ontology file not found at {owl_file_path}")
    exit()
except Exception as e:
    print(f"Error loading ontology: {e}")
    exit()


FoodRecipesIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodRecipes")
IngredientIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodIngredients")

if FoodRecipesIRI:
    recipes = list(onto.search(type=FoodRecipesIRI))
    print(f"FoodRecipes: {FoodRecipesIRI}")
    print(f"Number of recipes: {len(recipes)}")
else:
    print("FoodRecipes class not found in the ontology.")

if IngredientIRI:
    ingredients = list(onto.search(type=IngredientIRI))
    print(f"Ingredient: {IngredientIRI}")
    print(f"Number of ingredients: {len(ingredients)}")
else:
    print("FoodIngredients class not found in the ontology.")


def list_recipes(num_to_print=10):
        if FoodRecipesIRI:
            all_recipes = list(onto.search(type=FoodRecipesIRI))
            print(f"Number of individual recipes: {len(all_recipes)}")
            for recipe in all_recipes[:num_to_print]: # Print the first few
                if hasattr(recipe, 'label') and len(recipe.label) > 0:
                    print(f"- {recipe.label[0]}")
                elif hasattr(recipe, 'name'):
                    print(f"- {recipe.name}")
                else:
                    print(f"- {recipe}")
        else:
            print("FoodRecipes class not found in the ontology.")
