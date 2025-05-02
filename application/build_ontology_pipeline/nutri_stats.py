from owlready2 import get_ontology
import pandas as pd
import json
import os

# Load your ontology
owl_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline', 'nutri_mk_vri_recipe_nutrition_calculated.owl')
onto = get_ontology("file://" + owl_file_path ).load()


FoodRecipesIRI = onto.FoodRecipes
IngredientIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodIngredients")


ingredients = []
for ing in IngredientIRI.instances():
    label = ing.hasPrefLabel[0] if hasattr(ing, "hasPrefLabel") and ing.hasPrefLabel else ing.name
    ingredients.append(label)

# Remove duplicates and sort
ingredients = sorted(set(ingredients))



def extract_recipe_data(recipe):
    return {
        "name": recipe.name,
        "id": recipe.hasRecipeID[0] if hasattr(recipe, "hasRecipeID") and recipe.hasRecipeID else "NA",
        "url": recipe.hasRecipeURL[0] if hasattr(recipe, "hasRecipeURL") and recipe.hasRecipeURL else "NA",
        "ingredients": [
            i.name if hasattr(i, "name") else str(i)
            for i in recipe.hasIngredient
        ] if hasattr(recipe, "hasIngredient") else []
    }


# Extract all valid recipes
all_recipes = []
for r in FoodRecipesIRI.instances():
    if "FoodRecipes" not in [cls.name for cls in r.is_a]:
        continue
    all_recipes.append(extract_recipe_data(r))


base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline')
# Construct paths
recipe_csv_path = os.path.join(base_dir, "extracted_recipes_from_ontology.csv")
recipe_json_path = os.path.join(base_dir, "extracted_recipes_from_ontology.json")
ingredient_path = os.path.join(base_dir, "extracted_ingredients_from_ontology.json")
# Save the data
df = pd.DataFrame(all_recipes)
df.to_csv(recipe_csv_path, index=False)

with open(recipe_json_path, "w") as f:
    json.dump(all_recipes, f, indent=2)

with open(ingredient_path, "w") as f:
    json.dump(ingredients, f, indent=2)

print("\n✔️ Total ingredients:", len(ingredients))
print(f"Total recipes: {len(all_recipes)}\n\n")
print("🧂 Sample:", ingredients[:10])
