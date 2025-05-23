from owlready2 import get_ontology
import pandas as pd
import json
import os

owl_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline', 'nutri_mk_vri_recipe_nutrition_calculated.owl')
onto = get_ontology("file://" + owl_file_path ).load()


FoodRecipesIRI = onto.FoodRecipes
IngredientIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodIngredients")


ingredients = []
for ing in IngredientIRI.instances():
    label = ing.hasPrefLabel[0] if hasattr(ing, "hasPrefLabel") and ing.hasPrefLabel else ing.name
    ingredients.append(label)

ingredients = sorted(set(ingredients))

course_counts = {
        "Breakfast": 0,
        "Lunch": 0,
        "Snacks": 0,
        "Dinner": 0,
        "Other_or_No_Course": 0 
    }

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


print("Iterating through recipes...")
for r in FoodRecipesIRI.instances():
    if onto.FoodRecipes in r.is_a: 

        if hasattr(r, 'hasCourse') and r.hasCourse:
           
            courses = [str(course).lower() for course in r.hasCourse] 
            
            found_known_course = False
            if any("breakfast" in course for course in courses):
                course_counts["Breakfast"] += 1
                found_known_course = True
            if any("lunch" in course for course in courses):
                course_counts["Lunch"] += 1
                found_known_course = True
            if any("snacks" in course for course in courses):
                course_counts["Snacks"] += 1
                found_known_course = True
            if any("dinner" in course for course in courses):
                course_counts["Dinner"] += 1
                found_known_course = True
            
            if not found_known_course:
                course_counts["Other_or_No_Course"] +=1 
        else:
                course_counts["Other_or_No_Course"] += 1 

all_recipes = []
for r in FoodRecipesIRI.instances():
    if "FoodRecipes" not in [cls.name for cls in r.is_a]:
        continue
    all_recipes.append(extract_recipe_data(r))


base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline')
recipe_csv_path = os.path.join(base_dir, "extracted_recipes_from_ontology.csv")
recipe_json_path = os.path.join(base_dir, "extracted_recipes_from_ontology.json")
ingredient_path = os.path.join(base_dir, "extracted_ingredients_from_ontology.json")
df = pd.DataFrame(all_recipes)
df.to_csv(recipe_csv_path, index=False)

with open(recipe_json_path, "w") as f:
    json.dump(all_recipes, f, indent=2)

with open(ingredient_path, "w") as f:
    json.dump(ingredients, f, indent=2)

print("\nTotal ingredients:", len(ingredients))
print(f"Total recipes: {len(all_recipes)}\n\n")
print("\nRecipe counts by course:")
for course, count in course_counts.items():
     print(f"- {course}: {count}")
print("\nSample:", ingredients[:10])