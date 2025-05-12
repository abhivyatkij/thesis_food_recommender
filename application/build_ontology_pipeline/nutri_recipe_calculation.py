"""
This script takes the nutritional values of ingredients derived from the api and the indb and then calculates the recipe's nutriton. 
For example, if the recipe has ingredients x, with x having 10g of protein for 100g (as defined by indb)
But the recipe says that ing x is 200g, then the recipe's protein will be 20g. 
So it takes the ingredient weight and scale from the description and then proportionately appends that to the recipe
"""

import os
import ast
from owlready2 import *

build_ontology_pipeline_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline')
onto = get_ontology(os.path.join(build_ontology_pipeline_out_dir, 'mk_vri_json_api.owl')).load()

nutrient_map = {
    "hasEnergyKcal": "hasRecipeEnergyKcal",
    "hasCarbGram": "hasRecipeCarbGram",
    "hasProteinGram": "hasRecipeProteinGram",
    "hasFatGram": "hasRecipeFatGram",
    "hasFreeSugarGram": "hasRecipeFreeSugarGram",
    "hasFibreGram": "hasRecipeFibreGram",
    "hasSFAMGram": "hasRecipeSFAMGram",
    "hasMUFAMGram": "hasRecipeMUFAMGram",
    "hasPUFAMGram": "hasRecipePUFAMGram",
    "hasCholesterolMGram": "hasRecipeCholesterolMGram",
    "hasCalciumMGram": "hasRecipeCalciumMGram",
    "hasPhosphorusMGram": "hasRecipePhosphorusMGram",
    "hasMagnesiumMGram": "hasRecipeMagnesiumMGram",
    "hasSodiumMGram": "hasRecipeSodiumMGram",
    "hasPotassiumMGram": "hasRecipePotassiumMGram",
    "hasIronMGram": "hasRecipeIronMGram",
    "hasCopperMGram": "hasRecipeCopperMGram",
    "hasSeleniumUG": "hasRecipeSeleniumUG",
    "hasChromiumMGram": "hasRecipeChromiumMGram",
    "hasManganeseMGram": "hasRecipeManganeseMGram",
    "hasMolybdenumMGram": "hasRecipeMolybdenumMGram",
    "hasZincMGram": "hasRecipeZincMGram",
    "hasViteMGram": "hasRecipeViteMGram",
    "hasVitD2UG": "hasRecipeVitD2UG",
    "hasVitK1UG": "hasRecipeVitK1UG",
    "hasFolateUG": "hasRecipeFolateUG",
    "hasVitB1MGram": "hasRecipeVitB1MGram",
    "hasVitB2MGram": "hasRecipeVitB2MGram",
    "hasVitB3MGram": "hasRecipeVitB3MGram",
    "hasVitB5MGram": "hasRecipeVitB5MGram",
    "hasVitB6MGram": "hasRecipeVitB6MGram",
    "hasVitB7UG": "hasRecipeVitB7UG",
    "hasVitB9UG": "hasRecipeVitB9UG",
    "hasVitCMGram": "hasRecipeVitCMGram",
    "hasCarotenoidsUG": "hasRecipeCarotenoidsUG",
}

for recipe in onto.FoodRecipes.instances():
    totals = {prop: 0.0 for prop in nutrient_map.keys()}

    try:
        desc_raw  = recipe.hasIngredientDescription[0]
        parsed    = ast.literal_eval(desc_raw)
        raw_items = parsed[0].get("items", []) if parsed else []

        ingredient_data = {
            itm.get("name", "").strip().lower(): itm
            for itm in raw_items
            if isinstance(itm, dict)
        }
    except Exception:
        ingredient_data = {}


    for ing in getattr(recipe, "hasIngredient", []):
        if isinstance(ing, str):
            ing = onto.search_one(iri="*" + ing.split("#")[-1])
        if not ing:
            continue

        ing_name = ing.name.replace("_", " ").lower()
        ing_name_clean = ing_name.strip()
        weight = 100.0  

        if ing_name_clean == "salt":
            salt_info = ingredient_data.get("salt", {})
            salt_weight = salt_info.get("estimated_weight_in_grams", "NA")
            try:
                weight = float(salt_weight) if salt_weight != "NA" else 5.0
            except:
                weight = 5.0
        else:
            for key in ingredient_data:
                if key.lower().strip() in ing_name_clean:
                    try:
                        weight = float(ingredient_data[key].get("estimated_weight_in_grams", 100.0))
                    except:
                        weight = 100.0
                    break

        for ing_prop in nutrient_map:
            val = getattr(ing, ing_prop, None)
            if val:
                try:
                    scaled = (float(val[0]) / 100.0) * weight
                    totals[ing_prop] += scaled
                except:
                    continue

    for ing_prop, recipe_prop in nutrient_map.items():
        if totals[ing_prop] > 0:
            setattr(recipe, recipe_prop, [round(totals[ing_prop], 2)])

onto.save(os.path.join(build_ontology_pipeline_out_dir, "nutri_mk_vri_recipe_nutrition_calculated.owl"), format="rdfxml")
print("Saved updated recipe nutrition totals to nutri_mk_vri_recipe_nutrition_calculated.owl file.")
